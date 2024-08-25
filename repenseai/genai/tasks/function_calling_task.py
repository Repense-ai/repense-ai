from repenseai.genai.tasks.base_task import BaseTask
import importlib
import json
from repenseai.genai.api.openai import ChatAPI
from repenseai.utils.logs import logger


class FunctionCallingTask(BaseTask):
    """
    Represents a specific chatbot task that interprets a user's input within a context, formulates
    an instruction, and generates a response using a Large Language Model (LLM).

    Args:
        api (ChatAPI): model.
        prompt_template (str): Template to build the prompt for the task.
        function_map (dict): Mapping of function names to their implementations.
        tools (list): list of tools definition following openai format
        temperature (float, optional): Sampling temperature for model output. Defaults to 0.

    """

    def __init__(
        self,
        api: ChatAPI,
        prompt_template: str,
        instruction: str,
        function_map: dict,
        tools: list,
        temperature: float = 0,
    ) -> None:
        self.prompt_template = prompt_template
        self.instruction = instruction
        self.temperature = temperature
        self.function_map = function_map
        self.tools = tools
        self.model = api
        self.continue_interaction = True

    def _build_prompt(self, user_prompt, **kwargs):
        """
        Build the prompt for the task.

        Args:
            **kwargs: keyword arguments to be used in the prompt template.

        Returns:
            str: the prompt.
        """
        return [
            {
                "role": "system" if not user_prompt else "user",
                "content": self.prompt_template.format(
                    instruction=self.instruction, **kwargs
                ),
            }
        ]

    def _call_function_from_path(self, function_path, *args, **kwargs):
        # Split the path to extract module path and function name
        module_path, function_name = function_path.rsplit(".", 1)

        # Dynamically import the module
        module = importlib.import_module(module_path)

        # Get the function reference
        function = getattr(module, function_name)

        # Call the function with arguments
        return function(*args, **kwargs)

    def predict(self, context):
        """
        Handles the interaction loop with the LLM and processes function calls.

        Args:
            user_input (str): User's input message.
            context (dict): Contextual information for the LLM.
            function_map (dict): Mapping of function names to their implementations and extra arguments.

        Returns:
            str: The final response from the model.
        """
        messages = context.get("messages", [])
        user_input = context.get("user_text", "")
        self.continue_interaction = True
        if len(messages) == 0:
            prompt = self._build_prompt(
                prompt_template=self.prompt_template, user_prompt=False, **context
            )
            messages.append(prompt[0])
        if not messages:
            messages = []
        # logger("Processing user input: " + user_input)
        messages.append({"role": "user", "content": user_input})
        n_messages = context.get("n_messages", 10)
        context["messages"] = messages
        while self.continue_interaction:
            if len(messages) > n_messages + 1:
                if (
                    isinstance(messages[-n_messages:][0], dict)
                    and messages[-n_messages:][0].get("role") == "tool"
                ):
                    messages = [messages[0]] + messages[-n_messages + 1 :]
                else:
                    messages = [messages[0]] + messages[-n_messages:]

            response, raw_reponse = self._predict(context)

            # logger(
            #     "proposed function(s): "
            #     + str(response["choices"][0]["message"]["tool_calls"])
            # )

            messages.append(raw_reponse.choices[0].message)

            if response["choices"][0]["message"]["tool_calls"]:

                new_messages = self.handle_tool_calls(
                    response["choices"][0]["message"]["tool_calls"],
                    context,
                    self.function_map,
                )
                messages += new_messages
                context["messages"] = messages

                prompt = self._build_prompt(
                    prompt_template=self.prompt_template, user_prompt=False, **context
                )

                messages[0] = prompt[0]
            else:
                self.continue_interaction = False

        # TODO: get response text from model

        # print(context["messages"])
        return response["choices"][0]["message"]["content"]

    def _get_value_from_path(self, data_dict, path):
        # Split the path into components based on '.'
        keys = path.split(".")
        # Start with the initial dictionary
        current_data = data_dict
        try:
            # Iterate over each key in the path
            for key in keys:
                # Update the current_data to be the value associated with the current key
                current_data = current_data[key]
            # Return the value found at the end of the path
            return current_data
        except (KeyError, TypeError):
            # If the key is not found or the path is invalid (e.g., a string where a dict is expected)
            logger(f"Invalid path: {path}")
            return None  # Or handle the error as needed

    def handle_tool_calls(self, tool_calls, context, function_map):
        """
        Processes the tool calls and updates the context and interaction status.

        Args:
            tool_calls: Tool calls from the LLM response.
            context (dict): Contextual information for the LLM.
            function_map (dict): Mapping of function names to their implementations and extra arguments.
        """
        new_messages = []
        for call in tool_calls:
            result = self.execute_tool_call(call, function_map, context)
            # check if is session variable like session.cart_obj and update
            if function_map[call["function"]["name"]].get("output_variable"):
                for key in list(
                    function_map[call["function"]["name"]]["output_variable"].keys()
                ):
                    # we always pretend the output is a dict
                    # example  "output_variable": {"user_id": "user.id"}
                    context[key] = self._get_value_from_path(
                        result,
                        function_map[call["function"]["name"]]["output_variable"][key],
                    )

            new_messages.append(
                {
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": call["id"],
                    "name": call["function"]["name"],
                }
            )

            # TODO: Custom logic for handling specific tool responses

            self.continue_interaction = True
        return new_messages

    def execute_tool_call(self, tool_call, function_map, context):
        """
        Executes a specific tool call using the provided function map.

        Args:
            tool_call: The tool call to be executed.
            function_map (dict): Mapping of function names to their implementations and extra arguments.

        Returns:
            The result of the function call.
        """
        func_name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])
        if "extra_args" in function_map[func_name]:
            # first, check if is session variable like session.cart_obj and update
            for key, value in function_map[func_name]["extra_args"].items():
                if value.startswith("context."):
                    context_key = value.split(".")[1]
                    # TODO: i am keeping default value as empty dict
                    args[key] = context.get(context_key, {})
                else:
                    args[key] = value
        if func_name in function_map:
            return self._call_function_from_path(
                function_map[func_name]["function"], **args
            )
        else:
            raise ValueError(f"Function {func_name} not found.")

    def _predict(self, context: dict) -> str:
        """
        Generates a response to a given user input based on the task and context.

        Args:
            user_input (str): The input provided by the user.
            context (dict): Contextual information that influences the response.

        Returns:
            str: The response from the model.
        """
        try:
            self.model.call_api(context["messages"], functions=self.tools)

            tokens = self.model.get_tokens()

            full_response = self.model.get_response()
            raw_reponse = self.model.get_raw_response()
            text_response = self.model.get_text()
            if not text_response:
                text_response = self.model.get_function_blueprint() or ""

            # Sum tokens to context
            if "tokens" in context.keys():
                if self.model.model in context["tokens"].keys():
                    context["tokens"][self.model.model] += tokens
                else:
                    context["tokens"][self.model.model] = tokens
            else:
                context["tokens"] = {self.model.model: tokens}

            return full_response, raw_reponse
        except Exception as e:
            raise e
