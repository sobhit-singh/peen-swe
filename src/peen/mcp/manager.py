import asyncio
import contextlib
import os
import threading
from typing import Any

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError as e:
    raise ImportError(
        "The 'mcp' package is required to use MCP tools. "
        "Please install it with: pip install 'peen[mcp]'"
    ) from e

from peen.mcp.config import MCPConfig


class MCPManager:
    def __init__(self, config: MCPConfig | dict | None = None):
        if config is None:
            self.config = MCPConfig()
        elif isinstance(config, MCPConfig):
            self.config = config
        else:
            self.config = MCPConfig(**config)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._exit_stack: contextlib.AsyncExitStack | None = None
        self._sessions: dict[str, ClientSession] = {}
        self._tools: list[dict] = []
        self._lock = threading.RLock()

    def start(self, timeout: float = 30.0) -> None:
        """Start all configured MCP stdio servers."""
        if not self.config.servers:
            return
        with self._lock:
            if self._loop and self._loop.is_running():
                return
            self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            try:
                future = asyncio.run_coroutine_threadsafe(self._async_start(), self._loop)
                future.result(timeout=timeout)
            except Exception:
                self.close()
                raise

    def _run_loop(self) -> None:
        assert self._loop is not None
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _async_start(self) -> None:
        self._exit_stack = contextlib.AsyncExitStack()
        try:
            for name, server_cfg in self.config.servers.items():
                env = {**os.environ, **server_cfg.env} if server_cfg.env else None
                params = StdioServerParameters(command=server_cfg.command, args=server_cfg.args, env=env)
                read_stream, write_stream = await self._exit_stack.enter_async_context(stdio_client(params))
                session = await self._exit_stack.enter_async_context(ClientSession(read_stream, write_stream))
                await session.initialize()
                self._sessions[name] = session
        except Exception:
            await self._exit_stack.aclose()
            self._exit_stack = None
            self._sessions.clear()
            raise

    def get_tools(self, timeout: float = 15.0) -> list[dict]:
        """Fetch and return available tools from all connected MCP servers."""
        if not self._sessions:
            return []
        assert self._loop is not None
        future = asyncio.run_coroutine_threadsafe(self._async_get_tools(), self._loop)
        return future.result(timeout=timeout)

    async def _async_get_tools(self) -> list[dict]:
        tools = []
        for server_name, session in self._sessions.items():
            mcp_tools = await session.list_tools()
            for tool in mcp_tools.tools:
                schema = getattr(tool, "input_schema", getattr(tool, "inputSchema", {}))
                tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": f"{server_name}__{tool.name}",
                            "description": tool.description or "",
                            "parameters": schema if isinstance(schema, dict) else {},
                        },
                    }
                )
        return tools

    def execute(self, action: dict, timeout: float = 60.0) -> dict[str, Any]:
        """Execute an MCP tool action and return a standardized result dictionary."""
        tool_name = action.get("tool_name", "")
        if "__" not in tool_name:
            return {
                "output": "",
                "returncode": 1,
                "exception_info": f"Invalid MCP tool name: '{tool_name}'. Expected format: 'server__tool'.",
            }
        server_name, actual_name = tool_name.split("__", 1)
        session = self._sessions.get(server_name)
        if not session:
            return {
                "output": "",
                "returncode": 1,
                "exception_info": f"MCP server '{server_name}' is not connected.",
            }
        try:
            if not self._loop or not self._loop.is_running():
                raise RuntimeError("MCP event loop is not running")
            future = asyncio.run_coroutine_threadsafe(
                self._async_execute(session, actual_name, action.get("arguments", {})), self._loop
            )
            return future.result(timeout=timeout)
        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            return {
                "output": err_msg,
                "returncode": 1,
                "exception_info": f"MCP execution error: {err_msg}",
            }

    async def _async_execute(self, session: ClientSession, tool_name: str, arguments: dict) -> dict[str, Any]:
        try:
            result = await session.call_tool(tool_name, arguments=arguments)
            output_parts = []
            for block in getattr(result, "content", []):
                if hasattr(block, "text"):
                    output_parts.append(block.text)
                else:
                    output_parts.append(str(block))
            output_text = "\n".join(output_parts)
            is_error = getattr(result, "is_error", getattr(result, "isError", False))
            return {
                "output": output_text,
                "returncode": 1 if is_error else 0,
                "exception_info": output_text if is_error else "",
            }
        except Exception as e:
            err_msg = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
            return {
                "output": err_msg,
                "returncode": 1,
                "exception_info": f"MCP execution error: {err_msg}",
            }

    def close(self, timeout: float = 10.0) -> None:
        """Close all MCP sessions and shut down background runner."""
        with self._lock:
            if not self._loop or not self._loop.is_running():
                return
            try:
                future = asyncio.run_coroutine_threadsafe(self._async_close(), self._loop)
                future.result(timeout=timeout)
            except Exception:
                pass
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread:
                self._thread.join(timeout=timeout)
            self._loop = None
            self._thread = None

    async def _async_close(self) -> None:
        if self._exit_stack:
            await self._exit_stack.aclose()
            self._exit_stack = None
        self._sessions.clear()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
