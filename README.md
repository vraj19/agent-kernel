# AgentKernel
A small, lightweight execution layer that brings **determinism, structure and predictable behavior** to LangGraph based AI agents.

AgentKernel provides a simple, reliable, and structured runtime for **LangGraph**.
It defines the standard agent lifecycle, validates state transitions, enforces tool rules, and enables reproducible execution.

This project aims to make LangGraph agents **more predictable, easy to debug, and production-ready** by adding a kernel like execution layer underneath them.

## Why AgentKernel?
Langgraph is an incredible framework for building agent workflows, but:

- execution paths can be unpredictable
- state transitions depend on LLM behavior
- tools calls are not validated
- debugging multi-step flows is difficult
- reproducibility is limited
- replaying / auditing agent runs is hard

## What AgentKernel Provides

### 1. **Standard Agent Lifecycle**
Every run follows a simple state machine:
INIT -> PLAN -> ACT -> OBSERVE -> DECIDE -> END

### 2. **Deterministic Step Execution**
- each step runs in the correct order
- invalid transitions are blocked
- unexpected tool calls are prevented
- deterministic re-runs where possible (using the checkpoint)

### 3. **ToolRunner (Controlled Tool Execution)**
AgentKernel introduces a **ToolRunner** to explicitly manage tool execution.

- agents declare intent to use tools during the plan
- tools are executed only during the ACT
- tools must be explicitly registered by name
- execution is time bounded (threaded with timeouts)

This creates a separation between:
**agent reasoning** - what to do
**tool execution** - how it is done

```python
from agentkernel import ToolRunner

tool_runner = ToolRunner()
tool_runner.register("web_search", web_search_fn)
```
### 4. **Lightweight Tool Validation**
Before calling a tool, AgentKernel checks:

- required parameters
- correct types
- safety boundaries (timeout, cost caps)

### 5. **KernelNode (LangGraph Integration)**
A drop in node wrapper:

```python
from agentkernel import KernelNode
graph.add_node("agent", KernelNode(agent_logic))
```
This keeps all your LangGraph logic untouched, while adding structure under the hood.

### 6. **Replay Friendly Traces**
AgentKernel produces structured step traces that make debugging easier.


## What AgentKernel is NOT
- Not a framework
- Not a replacement for LangGraph
- Not a planner or multi-agent system
- Not a tracing platform

AgentKernel only adds structure and determinism to LangGraph nodes.


## Installation (Until PyPI release)

```python
pip install git+https://github.com/vraj19/agent-kernel.git
```
## License
MIT License.

## Contributions
Feedback, discussions, and contributions are welcome!

  
