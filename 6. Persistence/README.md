# Persistence Tutorial

This folder demonstrates state persistence and memory management in LangGraph workflows, showing how to save and restore workflow state across sessions.

## Tutorial Files

### Simple Persistence (`11. simple_persistence.ipynb`)

**Concepts Covered:**
- State persistence using checkpointers
- InMemorySaver for temporary storage
- Workflow state management across multiple executions
- Thread-based state isolation

**Code References:**
- `JokeState` class: Manages joke generation workflow state
  - `topic`: Input topic for joke generation
  - `joke`: Generated joke content
  - `explanation`: Detailed joke explanation
- `InMemorySaver()`: Checkpoint storage for state persistence
- `generate_joke()`: LLM-powered joke generation node
- `explain_joke()`: LLM-powered joke explanation node
- Workflow compilation with checkpointer: `workflow.compile(checkpointer=checkpoint)`

**Key Learning:**
- How to implement state persistence in LangGraph workflows
- Using checkpointers for workflow state management
- Thread-based state isolation and retrieval
- Multi-step workflow state preservation

---

## Full Code Walkthrough

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)

class JokeState(TypedDict):
  topic: str
  joke: str
  explanation: str

def generate_joke(state: JokeState):
  prompt = f"Generate a joke about the topic {state['topic']}"
  joke = model.invoke(prompt).content
  return {"joke": joke}

def explain_joke(state: JokeState):
  prompt = f"Explain the joke about the topic {state['topic']}: {state['joke']}"
  explanation = model.invoke(prompt).content
  return {"explanation": explanation}

graph = StateGraph(JokeState)
checkpoint = InMemorySaver()

graph.add_node("generate_joke", generate_joke)
graph.add_node("explain_joke", explain_joke)
graph.add_edge(START, "generate_joke")
graph.add_edge("generate_joke", "explain_joke")
graph.add_edge("explain_joke", END)

workflow = graph.compile(checkpointer=checkpoint)

config = {"configurable": {"thread_id": "1"}}
result = workflow.invoke({"topic": "chickens crossing the road"}, config=config)
print(result)

state = workflow.get_state(config)
print(state.values)              # Current state
print(list(workflow.get_state_history(config=config)))  # Historical checkpoints
```

### Execution Commentary
| Step | Action | State Update |
|------|--------|--------------|
| invoke | Provide initial input `{topic}` | Base state created |
| generate_joke | LLM generates `joke` | `{joke}` added |
| explain_joke | LLM explains the joke | `{explanation}` added |
| end | Final state persisted | All fields available |

## Why Persistence Matters
| Use Case | Benefit |
|----------|---------|
| Long-running generation | Recover after crash or restart |
| User sessions | Maintain continuity across requests |
| Auditing | Inspect historical node outputs |
| Branch exploration | Fork from earlier checkpoint |

## Inspecting State & History
```python
current = workflow.get_state(config)
print(current.next)   # Remaining nodes (empty at end)

history = list(workflow.get_state_history(config=config))
for snapshot in history:
  print(snapshot.values, snapshot.config)
```

## Adding More Nodes Safely
If you introduce a new downstream node (e.g. `rate_joke`) you can:
1. Add the node & edge.
2. Re-run `workflow.invoke(None, config=config)` to resume from last checkpoint (if graph semantics allow continuation).

## Switching Storage Backend (Pattern)
```python
# Pseudocode for a file-based saver (conceptual)
from langgraph.checkpoint.sqlite import SqliteSaver  # if available
checkpoint = SqliteSaver("checkpoints.db")
workflow = graph.compile(checkpointer=checkpoint)
```
Choose backend based on durability, scale, and concurrency requirements.

## Forking a Session
To branch from an intermediate state:
1. Retrieve history.
2. Select snapshot early in chain.
3. Start new thread with its values.
```python
snapshots = list(workflow.get_state_history(config=config))
base = snapshots[0].values
workflow.invoke(base, config={"configurable": {"thread_id": "fork_1"}})
```

## Defensive Patterns
| Risk | Mitigation |
|------|------------|
| Large state objects | Store references (IDs) instead of raw blobs |
| Sensitive data | Encrypt checkpoint payloads |
| Schema drift | Version fields + migration logic |
| Orphaned checkpoints | Periodic cleanup job |

## Enriching State with Metadata
Extend `JokeState`:
```python
class JokeState(TypedDict):
  topic: str
  joke: str
  explanation: str
  rating: int  # added later
```
When adding new fields ensure downstream nodes can handle absence (supply defaults where needed).

## Minimal Rating Extension
```python
def rate_joke(state: JokeState):
  joke = state["joke"]
  score = len(joke) % 10 + 1  # dummy heuristic
  return {"rating": score}

graph.add_node("rate_joke", rate_joke)
graph.add_edge("explain_joke", "rate_joke")
# Re-compile with same checkpointer
workflow = graph.compile(checkpointer=checkpoint)
workflow.invoke(None, config=config)  # continues at new node if logic permits
```

## Recovery Pattern After Interruption
```python
def safe_invoke(input_state, config):
  try:
    return workflow.invoke(input_state, config=config)
  except Exception as e:
    print("Error, resuming...")
    prior = workflow.get_state(config)
    # Possibly inspect prior.next to continue selectively
    raise e
```

## Summary
Persistence transforms ephemeral workflows into resilient, inspectable processes. With checkpointing you gain auditability, resumption, branching, and safer iteration over evolving graph designs.

## Workflow Architecture

### Persistence Flow Pattern
```
START
  ↓
generate_joke (with state save)
  ↓
explain_joke (with state save)
  ↓
END (final state persisted)
```

### State Persistence Cycle
```
Initial State → Node Execution → State Update → Checkpoint Save
     ↑                                                    ↓
State Recovery ←── Checkpoint Load ←── Session Resume ←──┘
```

## Key Concepts

### 1. **Checkpointing**
- Automatic state saving at each node execution
- Configurable checkpoint storage backends
- State recovery and resumption capabilities

### 2. **Thread Management**
- Thread-based state isolation
- Multiple concurrent workflow sessions
- Session-specific state management

### 3. **State Evolution**
- Progressive state updates through workflow
- Historical state tracking
- Rollback and recovery capabilities

### 4. **Memory Backends**
- `InMemorySaver`: Temporary in-memory storage
- Other backends: File-based, database-backed storage
- Configurable persistence strategies

## Implementation Details

### Checkpoint Configuration
```python
checkpoint = InMemorySaver()  # In-memory checkpoint storage
workflow = graph.compile(checkpointer=checkpoint)
```

### State Structure
```python
class JokeState(TypedDict):
    topic: str        # Input data
    joke: str         # Intermediate result
    explanation: str  # Final output
```

### Workflow Execution with Persistence
```python
# Execute workflow with state persistence
result = workflow.invoke(
    {"topic": "programming"}, 
    config={"configurable": {"thread_id": "joke_session_1"}}
)
```

## Features Demonstrated

### Automatic State Saving
- State automatically saved after each node execution
- No manual checkpoint management required
- Consistent state preservation

### Thread Isolation
- Multiple independent workflow sessions
- Thread-specific state management
- Concurrent execution support

### State Recovery
- Resume interrupted workflows
- Access historical state information
- Rollback to previous checkpoints

## Joke Generation Example

### Process Flow
1. **Input**: Topic for joke generation
2. **Generate Joke**: LLM creates joke based on topic
3. **State Save**: Joke content persisted to checkpoint
4. **Explain Joke**: LLM provides detailed explanation
5. **Final Save**: Complete state with joke and explanation saved

### State Evolution
```
Initial: {"topic": "programming"}
After generate_joke: {"topic": "programming", "joke": "Why do..."}
After explain_joke: {"topic": "programming", "joke": "Why do...", "explanation": "This joke..."}
```

## Prerequisites
- Python 3.8+
- LangGraph library with checkpoint support
- ChatGroq API access
- Understanding of basic LangGraph workflows
- dotenv for environment management

## Persistence Backends

### InMemorySaver
- **Use Case**: Development and testing
- **Characteristics**: Fast, temporary storage
- **Limitations**: Data lost on application restart

### File-based Storage
- **Use Case**: Local development with persistence
- **Characteristics**: Survives application restarts
- **Benefits**: Simple setup, no external dependencies

### Database Storage
- **Use Case**: Production applications
- **Characteristics**: Scalable, reliable, concurrent access
- **Benefits**: High availability, backup support

## Advanced Features

### State Inspection
```python
# Access saved state
saved_state = workflow.get_state(config)
print(saved_state.values)  # Current state values
print(saved_state.next)    # Next nodes to execute
```

### Workflow Resumption
```python
# Resume from checkpoint
continued_result = workflow.invoke(
    None,  # No new input needed
    config={"configurable": {"thread_id": "existing_session"}}
)
```

### Historical State Access
- View state at any checkpoint
- Analyze workflow progression
- Debug state changes

## Use Cases
- **Long-running Workflows**: Multi-step processes that need interruption handling
- **User Sessions**: Maintaining state across user interactions
- **Workflow Debugging**: Analyzing state changes and execution flow
- **Batch Processing**: Resumable data processing pipelines
- **Interactive Applications**: Stateful user experiences

## Running the Tutorial
1. Set up your environment and API keys
2. Execute the notebook cells in sequence
3. Observe state persistence across workflow steps
4. Experiment with different thread IDs
5. Try resuming workflows from checkpoints

## Best Practices
- Choose appropriate checkpoint storage for your use case
- Use meaningful thread IDs for session management
- Consider state size and storage limitations
- Implement proper error handling for persistence operations
- Plan for checkpoint cleanup and maintenance

## Common Patterns
- **Stateful Conversations**: Chatbots with memory
- **Multi-step Forms**: Progressive data collection
- **Workflow Orchestration**: Complex business processes
- **Data Processing Pipelines**: Resumable ETL operations

## Next Steps
After mastering basic persistence, explore:
- Advanced checkpoint strategies
- Custom checkpoint backends
- State migration and versioning
- Distributed workflow persistence
- Integration with external storage systems