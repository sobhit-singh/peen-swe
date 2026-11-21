from unittest.mock import MagicMock

from peen.agents.default import DefaultAgent


def test_default_agent_action_routing_bash_and_mcp():
    model = MagicMock()
    model.get_template_vars.return_value = {}
    model.serialize.return_value = {}
    model.format_observation_messages.side_effect = lambda msg, outputs, vars: [
        {"role": "tool", "content": o["output"]} for o in outputs
    ]

    env = MagicMock()
    env.get_template_vars.return_value = {}
    env.serialize.return_value = {}
    env.execute.return_value = {"output": "bash result", "returncode": 0}

    mcp_manager = MagicMock()
    mcp_manager.execute.return_value = {"output": "mcp result", "returncode": 0}

    agent = DefaultAgent(
        model=model,
        env=env,
        mcp_manager=mcp_manager,
        system_template="system",
        instance_template="instance",
    )

    message = {
        "role": "assistant",
        "extra": {
            "actions": [
                {"command": "echo 1"},
                {"tool_name": "fetch__url", "arguments": {"url": "http://test"}},
            ]
        },
    }

    obs = agent.execute_actions(message)

    # Bash action should be routed to env
    env.execute.assert_called_once_with({"command": "echo 1"})

    # MCP action should be routed to mcp_manager
    mcp_manager.execute.assert_called_once_with({"tool_name": "fetch__url", "arguments": {"url": "http://test"}})

    assert len(obs) == 2
    assert obs[0]["content"] == "bash result"
    assert obs[1]["content"] == "mcp result"


def test_default_agent_lifecycle():
    model = MagicMock()
    model.get_template_vars.return_value = {}
    model.serialize.return_value = {}
    model.format_message.return_value = {"role": "system", "content": "hi"}
    # Stop immediately
    model.query.return_value = {"role": "exit", "content": "done", "extra": {"exit_status": "done"}}

    env = MagicMock()
    env.get_template_vars.return_value = {}
    env.serialize.return_value = {}

    mcp_manager = MagicMock()
    mcp_manager.get_tools.return_value = [{"type": "function", "function": {"name": "test__t"}}]

    agent = DefaultAgent(
        model=model,
        env=env,
        mcp_manager=mcp_manager,
        system_template="system",
        instance_template="instance",
    )

    agent.run("do something")

    mcp_manager.start.assert_called_once()
    model.set_tools.assert_called_once()
    mcp_manager.close.assert_called_once()
