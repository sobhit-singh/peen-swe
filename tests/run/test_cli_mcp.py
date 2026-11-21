from unittest.mock import MagicMock, patch

from peen.run.mini import main


def test_cli_wires_mcp_config():
    with patch("peen.run.mini.configure_if_first_time"):
        with patch("peen.run.mini.get_model") as mock_get_model:
            with patch("peen.run.mini.get_environment") as mock_get_env:
                with patch("peen.run.mini.get_agent") as mock_get_agent:
                    mock_agent = MagicMock()
                    mock_get_agent.return_value = mock_agent

                    config_spec = [
                        "mini.yaml",
                        "mcp.servers.dummy.command=echo",
                    ]
                    main(
                        task="test task",
                        yolo=True,
                        config_spec=config_spec,
                    )

                    mock_get_agent.assert_called_once()
                    _, _, agent_kwargs = mock_get_agent.call_args[0]
                    assert "mcp_manager" in agent_kwargs
                    assert "dummy" in agent_kwargs["mcp_manager"].config.servers
