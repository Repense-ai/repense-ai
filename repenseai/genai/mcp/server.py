from typing import Optional, Dict, Any, List
import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class Server:
    def __init__(
        self, name: str, command: str, args: List[str], env: str | None = None
    ):
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
        self.is_connected = False

    async def connect(self):

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(self.server_params)
        )

        self.stdio, self.write = stdio_transport

        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()
        self.is_connected = True

    async def list_tools(self):
        if not self.is_connected:
            await self.connect()

        response = await self.session.list_tools()

        self.tools = response.tools
        self.tools_list = [tool.name for tool in self.tools]

        return self.tools

    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        return await self.session.call_tool(tool_name, tool_args)

    async def cleanup(self):
        try:
            # Ensure there's a running event loop
            loop = asyncio.get_running_loop()
            if loop.is_running():
                await self.exit_stack.aclose()
                self.is_connected = False
        except RuntimeError:
            # If no event loop is running, create one temporarily
            async def _cleanup():
                await self.exit_stack.aclose()
                self.is_connected = False

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(_cleanup())
            finally:
                loop.close()
                asyncio.set_event_loop(None)
