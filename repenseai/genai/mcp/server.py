from typing import Optional, Dict, Any, List
import asyncio
import logging
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool


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
            
        try:
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(self.server_params)
            )

            self.stdio, self.write = stdio_transport

            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            await self.session.initialize()
            self.is_connected = True
        except Exception as e:
            logging.error(f"Error connecting to server {self.name}: {str(e)}")
            # Garantir que todos os recursos sejam liberados em caso de erro
            await self.cleanup()
            raise

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
            
        # Simplesmente limpe usando o loop atual
        try:
            await self.exit_stack.aclose()
            self.is_connected = False
        except Exception as e:
            logging.error(f"Error during server cleanup: {str(e)}")
            # Certifique-se que o servidor é marcado como desconectado
            self.is_connected = False


class ServerManager:
    def __init__(self, servers: List[Server] = None):
        self.servers = servers or []
        self.tool_to_server_map = {}
        self.all_tools = []
        self.all_tools_list = []
        self.initialized = False
    
    def add_server(self, server: Server):
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
            # Use gather with return_exceptions=True para evitar falhas cascata
            results = await asyncio.gather(*connection_tasks, return_exceptions=True)
            # Verificar se alguma conexão falhou
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logging.error(f"Failed to connect to server: {str(result)}")
            
        # List tools from all servers concurrently
        tools_tasks = [server.list_tools() for server in self.servers if server.is_connected]
        all_server_tools = await asyncio.gather(*tools_tasks, return_exceptions=True)
        
        # Map each tool to its server
        for i, server_tools in enumerate(all_server_tools):
            if isinstance(server_tools, Exception):
                continue
                
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
        cleanup_tasks = []
        for server in self.servers:
            if server.is_connected:
                cleanup_tasks.append(server.cleanup())
                
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)