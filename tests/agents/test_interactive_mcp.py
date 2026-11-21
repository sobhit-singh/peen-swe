from unittest.mock import MagicMock, patch

from peen.agents.interactive import InteractiveAgent


def test_interactive_agent_handles_mcp_actions_in_yolo():
    model = MagicMock()
    model.get_template_vars.return_value = {}
    model.serialize.return_value = {}
    model.format_observation_messages.side_effect = lambda msg, outputs, vars: [
        {"role": "tool", "content": o["output"]} for o in outputs
    ]

    env = MagicMock()
    env.get_template_vars.return_value = {}
    env.serialize.return_value = {}
    env.execute.return_value = {"output": "bash done", "returncode": 0}

    mcp_manager = MagicMock()
    mcp_manager.execute.return_value = {"output": "mcp done", "returncode": 0}

    agent = InteractiveAgent(
        model=model,
        env=env,
        mcp_manager=mcp_manager,
        mode="yolo",
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

    env.execute.assert_called_once_with({"command": "echo 1"})
    mcp_manager.execute.assert_called_once_with({"tool_name": "fetch__url", "arguments": {"url": "http://test"}})
    assert len(obs) == 2


def test_interactive_agent_confirm_mcp_action():
    model = MagicMock()
    model.get_template_vars.return_value = {}
    model.serialize.return_value = {}
    model.format_observation_messages.side_effect = lambda msg, outputs, vars: [
        {"role": "tool", "content": o["output"]} for o in outputs
    ]

    env = MagicMock()
    mcp_manager = MagicMock()
    mcp_manager.execute.return_value = {"output": "mcp done", "returncode": 0}

    agent = InteractiveAgent(
        model=model,
        env=env,
        mcp_manager=mcp_manager,
        mode="confirm",
        system_template="system",
        instance_template="instance",
    )

    message = {
        "role": "assistant",
        "extra": {
            "actions": [
                {"tool_name": "fetch__url", "arguments": {"url": "http://test"}},
            ]
        },
    }

    with patch.object(agent, "_prompt_and_handle_slash_commands", return_value=""):
        obs = agent.execute_actions(message)

    mcp_manager.execute.assert_called_once()
    assert len(obs) == 1
    assert obs[0]["content"] == "mcp done"


def test_interactive_agent_empty_bash_command_not_mcp():
    model = MagicMock()
    model.get_template_vars.return_value = {}
    model.serialize.return_value = {}
    model.format_observation_messages.return_value = []

    env = MagicMock()
    agent = InteractiveAgent(
        model=model,
        env=env,
        mode="yolo",
        system_template="system",
        instance_template="instance",
    )

    message = {"role": "assistant", "extra": {"actions": [{"command": ""}]}}
    agent.execute_actions(message)
    env.execute.assert_called_once_with({"command": ""})
