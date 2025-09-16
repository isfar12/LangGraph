# Custom React Agent Implementation

This folder contains a complete implementation of a custom React (Reasoning and Acting) agent built from scratch using LangGraph, demonstrating manual control over agent behavior and tool execution.

## Files Overview

### Core Implementation Files

#### `react_state.py`
**Purpose:** Defines the state structure for the React agent
**Code References:**
- `ReactAgentState` class: TypedDict containing agent state
- `input`: String field for user queries
- `agent_outcome`: Union of AgentAction, AgentFinish, or None
- `intermediate_steps`: Annotated list tracking action-observation pairs

```python
import operator
from typing import Annotated, TypedDict, Union
from langchain_core.agents import AgentAction, AgentFinish

class ReactAgentState(TypedDict):
  input: str
  agent_outcome: Union[AgentAction, AgentFinish, None]
  # Annotated list with an "add" reducer so each node can append a tuple (Action, Observation)
  intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]
```

Explanation:
- `Annotated[..., operator.add]` tells LangGraph how to merge partial updates: new lists are concatenated rather than overwritten.
- `agent_outcome` holds either the next tool call instruction (`AgentAction`) or the final answer wrapper (`AgentFinish`).
- `intermediate_steps` is the ReAct scratchpad you would normally embed inside the prompt; here it's explicit state.

#### `agent_reason_runnable.py`
**Purpose:** Sets up the reasoning component and tools
**Code References:**
- `ChatGroq` LLM configuration with llama-3.3-70b-versatile
- `TavilySearch` tool for web searches
- `current_time()`: Custom tool decorated with @tool
- `create_react_agent()`: Creates agent with prompt from LangChain hub
- Tools list: `[search_tool, current_time]`

```python
from langchain.agents import create_react_agent, tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain import hub
import datetime

search_tool = TavilySearch()  # external search capability
llm = ChatGroq(model="llama-3.3-70b-versatile")

@tool
def current_time() -> str:
  """Get the current time."""
  return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools = [search_tool, current_time]
prompt = hub.pull("hwchase17/react")  # canonical ReAct template
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
```

Explanation:
- `@tool` decorator auto-wraps the function with metadata so the agent can select it.
- The pulled hub prompt expects a format including prior actions & observations; LangChain handles that internally when using `create_react_agent`.
- The resulting `agent` is a Runnable — it can be placed directly into a LangGraph node.

#### `nodes.py`
**Purpose:** Implements the core workflow nodes
**Code References:**
- `reason_node(state)`: Invokes agent to determine next action
- `act_node(state)`: Executes tools and returns observations
- Manual tool lookup and execution logic
- Tool input handling for both dict and string formats

```python
from agent_reason_runnable import agent, tools
from react_state import ReactAgentState

def reason_node(state: ReactAgentState):
  # Pass the whole state; agent will read needed keys (notably prior intermediate steps if integrated)
  agent_outcome = agent.invoke(state)
  return {"agent_outcome": agent_outcome}

def act_node(state: ReactAgentState):
  agent_action = state["agent_outcome"]  # must be AgentAction here
  tool_name = agent_action.tool
  tool_input = agent_action.tool_input

  # Manual lookup (alternative to a centralized ToolExecutor)
  selected = next((t for t in tools if t.name == tool_name), None)
  if not selected:
    observation = f"Tool {tool_name} not found."
  else:
    # Tools may expect kwargs or a raw input string
    if isinstance(tool_input, dict):
      observation = selected.invoke(**tool_input)
    else:
      observation = selected.invoke(tool_input)

  return {"intermediate_steps": [(agent_action, str(observation))]}
```

Explanation:
- `reason_node` isolates reasoning (deciding which tool to call or finishing).
- `act_node` performs the chosen action and records the observation.
- Separation keeps logic clean & testable: you can unit test tool execution independent of reasoning.
- Returning only partial state updates (dict diff) allows LangGraph to merge without clobbering other fields.

#### `react_graph.py`
**Purpose:** Orchestrates the complete workflow
**Code References:**
- `should_continue()`: Conditional logic for workflow control
- Graph structure: START → REASON_NODE → (ACT_NODE ↔ REASON_NODE) → END
- `StateGraph(ReactAgentState)` setup
- Conditional edges based on `AgentFinish` vs `AgentAction`

```python
from langgraph.graph import StateGraph, START, END
from langchain_core.agents import AgentFinish
from react_state import ReactAgentState
from nodes import reason_node, act_node

REASON_NODE = "reason_node"
ACT_NODE = "act_node"

def should_continue(state: ReactAgentState):
  # If the agent produced a final answer, terminate; else go execute the tool
  return END if isinstance(state["agent_outcome"], AgentFinish) else ACT_NODE

graph = StateGraph(ReactAgentState)
graph.add_node(REASON_NODE, reason_node)
graph.add_node(ACT_NODE, act_node)
graph.add_edge(START, REASON_NODE)
graph.add_conditional_edges(REASON_NODE, should_continue)
graph.add_edge(ACT_NODE, REASON_NODE)  # loop back for further reasoning
workflow = graph.compile()

result = workflow.invoke({"input": "What time is it and what is the capital of France?"})
print(result)
```

Explanation:
- `add_conditional_edges` enables loop vs termination without imperative loops.
- The `ACT_NODE → REASON_NODE` edge re-enters the reasoning cycle with new context (the latest tool result in `intermediate_steps`).
- Loop ends naturally when the agent produces an `AgentFinish`.

## Workflow Architecture

```
START
  ↓
REASON_NODE (Agent decides action)
  ↓
should_continue() decision
  ↓
├─ AgentFinish → END
└─ AgentAction → ACT_NODE (Execute tool)
                    ↓
                 REASON_NODE (Continue reasoning)
```

## Key Concepts Demonstrated

### 1. **Manual Tool Execution**
- Alternative to `ToolExecutor` 
- Direct tool lookup and invocation
- Error handling for unknown tools

### 2. **State Management**
- Tracking intermediate steps with `operator.add`
- Preserving agent reasoning history
- State updates through return dictionaries

### 3. **Conditional Workflow**
- Dynamic routing based on agent outcomes
- Loop continuation until task completion
- Proper termination handling

### 4. **Custom Agent Architecture**
- Full control over agent behavior
- Modular design with separated concerns
- Extensible tool integration

## Code Patterns

### State Updates
```python
# In nodes.py - proper state update pattern
return {"agent_outcome": agent_outcome}
return {"intermediate_steps": [(agent_action, str(observation))]}
```

### Tool Execution Pattern
```python
# Manual tool lookup alternative to ToolExecutor
tool_function = None
for tool in tools:
    if tool.name == tool_name:
        tool_function = tool
        break
```

### Conditional Routing
```python
def should_continue(state: ReactAgentState):
    if isinstance(state["agent_outcome"], AgentFinish):
        return END
    else:
        return ACT_NODE
```

## Prerequisites
- Python 3.8+
- LangGraph library
- LangChain and LangChain-Groq
- TavilySearch API access
- dotenv for environment management

## Running the Implementation
1. Set up API keys in `.env` file
2. Execute `python react_graph.py`
3. Observe agent reasoning through tool usage
4. Check ASCII graph output with `workflow.draw_ascii()`

## Advanced Features
- **Tool Input Flexibility**: Handles both dict and string tool inputs
- **Error Handling**: Graceful handling of unknown tools
- **Debugging Support**: Verbose intermediate step tracking
- **Modular Design**: Easy to extend with new tools and capabilities

## Comparison with Built-in Agents
- **More Control**: Full visibility and control over agent behavior
- **Customization**: Easy to modify reasoning or tool execution logic
- **Learning**: Better understanding of agent internals
- **Flexibility**: Can implement custom tool selection strategies

This implementation serves as a foundation for building more sophisticated agent systems with custom behavior patterns.

## Debugging & Extension Tips

| Goal | Suggested Change |
|------|------------------|
| Add logging of each cycle | Append a `cycle_count` field to state and increment in `reason_node` |
| Enforce max tool calls | Add a conditional edge guard that routes to END after N loops |
| Inject memory | Add a `memory` list field annotated with `operator.add` and push summaries each cycle |
| Swap LLM | Replace `ChatGroq` with any `langchain_core` compatible chat model |
| Add retry on tool failure | Wrap `selected.invoke` in try/except and append an error observation |

### Converting to Pure Diff Updates
If you prefer functional purity, refactor nodes to never mutate the original state object; always return only changed keys (already done in the shown patterns). This makes reasoning about state transitions easier and reduces accidental overwrites.

### Visualizing the Graph
After compilation:
```python
print(workflow.draw_ascii())
```
Useful for confirming loops & termination edges.

### Testing Strategy
1. Unit test `reason_node` with a mocked agent producing an `AgentAction`.
2. Unit test `act_node` with a fabricated `AgentAction` referencing a stub tool.
3. Integration test the entire loop with deterministic tool outputs.

---
With these internals documented, you can safely extend the system into more sophisticated multi-tool or multi-agent orchestration patterns.