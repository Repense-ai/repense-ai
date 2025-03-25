from typing import Optional, Dict, Any, List

from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class Server:
    def __init__(self, name: str, command: str, args: List[str], env: str| None = None): 
        self.name = name

        self.server_params = StdioServerParameters(
            command=command,
            args=args,
            env=env,
        )

        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        self.tools = None
        self.tools_list = None
        self.stdio = None
        self.write = None

    async def connect(self):
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(self.server_params)
        )

        self.stdio, self.write = stdio_transport

        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()
        response = await self.session.list_tools()
        
        self.tools = response.tools
        self.tools_list = [tool.name for tool in self.tools]

        return self.tools

    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        return await self.session.call_tool(tool_name, tool_args)

    async def cleanup(self):
        await self.exit_stack.aclose()