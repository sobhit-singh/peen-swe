from unittest.mock import MagicMock, patch

from peen.run.peen import main


def test_peen_cli_wires_task_and_mcp_config():
    with patch("peen.run.peen.configure_if_first_time"):
        with patch("peen.run.peen.get_model") as mock_get_model:
            with patch("peen.run.peen.get_environment") as mock_get_env:
                with patch("peen.run.peen.get_agent") as mock_get_agent:
                    mock_agent = MagicMock()
                    mock_get_agent.return_value = mock_agent

                    config_spec = [
                        "peen.yaml",
                        "mcp.servers.dummy.command=echo",
                    ]
                    main(
                        task="refactor test task",
                        yolo=True,
                        config_spec=config_spec,
                    )

                    mock_get_agent.assert_called_once()
                    _, _, agent_kwargs = mock_get_agent.call_args[0]
                    assert "mcp_manager" in agent_kwargs
                    assert "dummy" in agent_kwargs["mcp_manager"].config.servers
                    mock_agent.run.assert_called_once_with("refactor test task")
