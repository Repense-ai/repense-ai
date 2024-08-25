from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import Function


def serialize_message(obj):
    if isinstance(obj, ChatCompletionMessage):
        out_dict = {
            "content": obj.content,
            "role": obj.role,
        }
        if "function_call" in dict(obj):
            out_dict["function_call"] = serialize_message(obj.function_call)
        if "tool_calls" in dict(obj):
            out_dict["tool_calls"] = serialize_message(obj.tool_calls)
        return out_dict
    elif isinstance(obj, ChatCompletionMessageToolCall):
        return {
            "id": obj.id,
            "function": {
                "name": obj.function.name,
                "arguments": obj.function.arguments,
            },
            "type": obj.type,
        }
    elif isinstance(obj, dict):
        return {key: serialize_message(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_message(item) for item in obj]
    else:
        return obj


def deserialize_message(serialized_obj):
    if isinstance(serialized_obj, dict):
        if "role" in serialized_obj:
            role = serialized_obj.get("role")
            if role == "assistant":
                # Deserialize as ChatCompletionMessage only if the role is 'assistant'
                out = ChatCompletionMessage(
                    content=serialized_obj.get("content"),
                    role=role,
                    function_call=deserialize_message(
                        serialized_obj.get("function_call")
                    ),
                    tool_calls=deserialize_message(serialized_obj.get("tool_calls")),
                )
                if serialized_obj.get("tool_calls") and serialized_obj.get(
                    "function_call"
                ):
                    out = ChatCompletionMessage(
                        content=serialized_obj.get("content"),
                        role=role,
                        function_call=deserialize_message(
                            serialized_obj.get("function_call")
                        ),
                        tool_calls=deserialize_message(
                            serialized_obj.get("tool_calls")
                        ),
                    )

                if out.content is None:
                    out.content = ""
                if out.function_call is None:
                    del out.function_call
                if out.tool_calls is None:
                    del out.tool_calls
                return out
            else:
                # For other roles, return the dictionary as is
                return serialized_obj
        elif "id" in serialized_obj and "function" in serialized_obj:
            function_data = serialized_obj.get("function")
            return ChatCompletionMessageToolCall(
                id=serialized_obj.get("id"),
                function=Function(
                    name=function_data.get("name"),
                    arguments=function_data.get("arguments"),
                ),
                type=serialized_obj.get("type"),
            )
        else:
            return {
                key: deserialize_message(value) for key, value in serialized_obj.items()
            }
    elif isinstance(serialized_obj, list):
        return [deserialize_message(item) for item in serialized_obj]
    else:
        return serialized_obj
