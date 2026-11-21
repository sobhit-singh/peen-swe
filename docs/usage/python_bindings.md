# Python Bindings

Peen-SWE can be embedded directly into Python applications, evaluation harnesses, and test automation pipelines.

---

## Basic Execution

Instantiate a model, an environment, and `DefaultAgent`:

```python
import logging
from peen.agents.default import DefaultAgent
from peen.environments.local import LocalEnvironment
from peen.models import get_model

logging.basicConfig(level=logging.INFO)

# 1. Initialize language model
model = get_model(input_model_name="anthropic/claude-3-5-sonnet-20241022")

# 2. Configure execution sandbox (LocalEnvironment, DockerEnvironment, etc.)
env = LocalEnvironment()

# 3. Create and execute agent
agent = DefaultAgent(model, env)
result = agent.run("Find all TODO comments in src/ and output a summary")
print(f"Agent finished with exit status: {result['exit_status']}")
```

---

## Programmatic MCP Integration

Peen-SWE allows injecting Model Context Protocol (MCP) server managers programmatically. Tools exposed by MCP servers are automatically routed through stdio and made available alongside bash:

```python
from peen.agents.default import DefaultAgent
from peen.environments.local import LocalEnvironment
from peen.mcp.manager import MCPManager
from peen.models import get_model

# Initialize MCP manager with SQLite or custom tool servers
mcp_manager = MCPManager.from_dict({
    "sqlite": {
        "command": "uvx",
        "args": ["mcp-server-sqlite", "--db-path", "app.db"]
    }
})

agent = DefaultAgent(
    model=get_model("anthropic/claude-3-5-sonnet-20241022"),
    env=LocalEnvironment(),
    mcp_manager=mcp_manager,
)

# Tools from 'sqlite' are now available to the agent
agent.run("Inspect the schema of app.db and add an index on user_id")
```

---

## Capturing Trajectories & Cost

`agent.run()` returns the final state, while `agent.messages` stores the complete trajectory history:

```python
# Access aggregated execution metrics
stats = model.stats
print(f"Total API calls: {stats.api_calls}")
print(f"Total session cost: ${stats.instance_cost:.4f}")

# Inspect raw message history and tool calls
for msg in agent.messages:
    role = msg.get("role")
    if role == "assistant":
        print(f"[Assistant] {msg.get('content')}")
        if "extra" in msg:
            print(f"Executed: {msg['extra'].get('actions')}")
```

For subclassing custom agents, creating customized observation filters, or using Docker sandboxes, see the [Cookbook](../advanced/cookbook.md).

{% include-markdown "../_footer.md" %}
