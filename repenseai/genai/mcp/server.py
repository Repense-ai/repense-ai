from typing import Optional, Dict, Any, List, Union
import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool


class ServerManager:
    def __init__(self, servers: List['Server'] = None):
        self.servers = servers or []
        self.tool_to_server_map = {}
        self.all_tools = []
        self.all_tools_list = []
        self.initialized = False
    
    def add_server(self, server: 'Server'):
        """Add a server to the manager."""
        self.servers.append(server)
        self.initialized = False
    
    async def initialize(self):
        """Connect to all servers and map tools to their servers."""
        if self.initialized:
            return
            
        self.tool_to_server_map = {}
        self.all_tools = []
        self.all_tools_list = []
        
        # Connect to all servers and collect their tools concurrently
        connection_tasks = [server.connect() for server in self.servers if not server.is_connected]
        if connection_tasks:
            await asyncio.gather(*connection_tasks)
            
        # List tools from all servers concurrently
        tools_tasks = [server.list_tools() for server in self.servers]
        all_server_tools = await asyncio.gather(*tools_tasks)
        
        # Map each tool to its server
        for i, server_tools in enumerate(all_server_tools):
            server = self.servers[i]
            for tool in server_tools:
                self.all_tools.append(tool)
                self.all_tools_list.append(tool.name)
                self.tool_to_server_map[tool.name] = server
                
        self.initialized = True
        
    async def get_all_tools(self) -> List[Tool]:
        """Get a list of all tools from all servers."""
        if not self.initialized:
            await self.initialize()
        return self.all_tools
    
    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Call a tool by name with the given arguments."""
        if not self.initialized:
            await self.initialize()
            
        if tool_name not in self.tool_to_server_map:
            raise ValueError(f"Tool '{tool_name}' not found in any server")
            
        server = self.tool_to_server_map[tool_name]
        return await server.call_tool(tool_name, args)
        
    async def cleanup(self):
        """Clean up all server connections."""
        cleanup_tasks = [server.cleanup() for server in self.servers]
        await asyncio.gather(*cleanup_tasks)


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
        if self.is_connected:
            return
            
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
        if not self.is_connected:
            await self.connect()
        return await self.session.call_tool(tool_name, tool_args)

    async def cleanup(self):
        if not self.is_connected:
            return
            
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