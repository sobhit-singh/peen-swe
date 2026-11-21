from peen.mcp.config import MCPConfig, MCPServerConfig


def test_mcp_server_config():
    cfg = MCPServerConfig(command="uvx", args=["mcp-server-fetch"], env={"KEY": "VAL"})
    assert cfg.command == "uvx"
    assert cfg.args == ["mcp-server-fetch"]
    assert cfg.env == {"KEY": "VAL"}


def test_mcp_config_defaults():
    cfg = MCPConfig()
    assert cfg.servers == {}


def test_mcp_config_parsing():
    data = {"servers": {"fetch": {"command": "uvx", "args": ["mcp-server-fetch"]}}}
    cfg = MCPConfig(**data)
    assert "fetch" in cfg.servers
    assert cfg.servers["fetch"].command == "uvx"
    assert cfg.servers["fetch"].args == ["mcp-server-fetch"]
