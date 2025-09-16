# Parallel Workflow Tutorials

This folder demonstrates how to build parallel execution workflows in LangGraph, where multiple nodes can execute simultaneously to improve performance and efficiency.

## Tutorial Files

### 1. Parallel Workflow (`4.parallel_workflow.ipynb`)
**Concepts Covered:**
- Parallel node execution in LangGraph
- Independent calculations running simultaneously
- State management for parallel operations
- Performance optimization through concurrency

**Code References:**
- `BatsManState` class: Cricket batsman statistics state
- `calculate_strike_rate()`: Computes batting strike rate
- `calculate_boundary_percent()`: Calculates boundary scoring percentage
- `calculate_balls_per_boundary()`: Determines balls per boundary ratio
- `calculate_summary()`: Aggregates all statistics
- Parallel node execution pattern

**Key Learning:**
- How to design workflows for parallel execution
- Independent node operations that don't depend on each other
- State updates from multiple concurrent nodes
- Performance benefits of parallel processing

**Full Code Walkthrough:**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class BatsManState(TypedDict):
  runs: int
  balls: int
  six: int
  fours: int
  strike_rate: float
  boundary_percent: float
  balls_per_boundary: float
  summary: str

def calculate_strike_rate(state: BatsManState):
  if state['balls'] == 0:
    return {"strike_rate": 0.0}
  return {"strike_rate": (state['runs'] / state['balls']) * 100}

def calculate_boundary_percent(state: BatsManState):
  if state['runs'] == 0:
    return {"boundary_percent": 0.0}
  return {"boundary_percent": ((state['fours'] + state['six']) / state['runs']) * 100}

def calculate_balls_per_boundary(state: BatsManState):
  if state['fours'] + state['six'] == 0:
    return {"balls_per_boundary": 0.0}
  return {"balls_per_boundary": state['balls'] / (state['fours'] + state['six'])}

def calculate_summary(state: BatsManState):
  # Use previously computed metrics (which may arrive from parallel nodes)
  summary = f"Strike Rate: {state.get('strike_rate')}\n" \
        f"Boundary %: {state.get('boundary_percent')}\n" \
        f"Balls/Boundary: {state.get('balls_per_boundary')}"
  return {"summary": summary}

graph = StateGraph(BatsManState)
graph.add_node("calculate_strike_rate", calculate_strike_rate)
graph.add_node("calculate_boundary_percent", calculate_boundary_percent)
graph.add_node("calculate_balls_per_boundary", calculate_balls_per_boundary)
graph.add_node("calculate_summary", calculate_summary)

# START fans out to three independent metric nodes
graph.add_edge(START, "calculate_strike_rate")
graph.add_edge(START, "calculate_boundary_percent")
graph.add_edge(START, "calculate_balls_per_boundary")

# All three converge into the summary node
graph.add_edge("calculate_strike_rate", "calculate_summary")
graph.add_edge("calculate_boundary_percent", "calculate_summary")
graph.add_edge("calculate_balls_per_boundary", "calculate_summary")
graph.add_edge("calculate_summary", END)

workflow = graph.compile()
final_state = workflow.invoke({
  "runs": 72,
  "balls": 50,
  "six": 3,
  "fours": 6
})
print(final_state["summary"])
```

Explanation:
- Three metric nodes do not depend on each other → eligible for parallel scheduling.
- Each returns only its own field(s) (partial state diff) → safe concurrent merging.
- The `calculate_summary` node runs once all predecessor nodes have produced their updates.
- LangGraph internally handles readiness: a node executes when all its inbound edges have emitted.

Common Pitfall: Avoid having parallel nodes write the same key unless you use a reducer (e.g. `Annotated[..., operator.add]`). Otherwise last writer wins.

Adding a Reducer Example:
```python
from typing import Annotated
import operator
class MetricsState(TypedDict):
  metrics: Annotated[list[str], operator.add]
```
Then each parallel node can safely return `{"metrics": ["some text"]}` and LangGraph concatenates lists.

### 2. Parallel Workflow with LLM (`5.parallel_workfloiw_llm.ipynb`)
**Concepts Covered:**
- Parallel LLM operations
- Concurrent content generation
- Multi-prompt processing
- Aggregating results from parallel LLM calls

**Code References:**
- Multiple LLM nodes executing in parallel
- Independent prompt processing
- Result aggregation patterns
- ChatGroq integration for parallel calls

**Key Learning:**
- How to parallelize LLM operations
- Managing multiple concurrent API calls
- Aggregating and combining parallel results
- Optimizing LLM workflows for speed

**Illustrative Pattern (Pseudo-Implementation):**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_groq import ChatGroq

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.4)

class IdeasState(TypedDict):
  topic: str
  hook: str
  outline: str
  title_options: list[str]
  combined: str

def gen_hook(state: IdeasState):
  prompt = f"Write a compelling opening hook about {state['topic']}"
  return {"hook": model.invoke(prompt).content}

def gen_outline(state: IdeasState):
  prompt = f"Create a concise outline about {state['topic']}"
  return {"outline": model.invoke(prompt).content}

def gen_titles(state: IdeasState):
  prompt = f"Suggest 5 catchy titles about {state['topic']} as a JSON list"
  raw = model.invoke(prompt).content
  # (Parsing omitted for brevity)
  return {"title_options": [t.strip() for t in raw.split('\n') if t][:5]}

def combine(state: IdeasState):
  prompt = (
    f"Using this hook: {state['hook']}\nOutline: {state['outline']}\n"
    f"Titles: {state['title_options']}\nCraft a refined summary paragraph."
  )
  return {"combined": model.invoke(prompt).content}

graph = StateGraph(IdeasState)
graph.add_node("gen_hook", gen_hook)
graph.add_node("gen_outline", gen_outline)
graph.add_node("gen_titles", gen_titles)
graph.add_node("combine", combine)

graph.add_edge(START, "gen_hook")
graph.add_edge(START, "gen_outline")
graph.add_edge(START, "gen_titles")
graph.add_edge("gen_hook", "combine")
graph.add_edge("gen_outline", "combine")
graph.add_edge("gen_titles", "combine")
graph.add_edge("combine", END)

workflow = graph.compile()
result = workflow.invoke({"topic": "Quantum Computing for Beginners"})
print(result["combined"])
```

Explanation:
- The three generation nodes run in parallel, reducing overall latency compared to sequential execution.
- The `combine` node waits until all required upstream keys (`hook`, `outline`, `title_options`) are present.
- Useful pattern for multi-perspective synthesis: collect diverse outputs then harmonize.

Enhancements:
- Add validation nodes to sanitize or parse structured JSON output.
- Introduce caching layer for repeated prompts.
- Enforce timeouts or fallbacks if one parallel branch is slow.

## Workflow Architecture

### Parallel Execution Pattern
```
START
  ↓
Initial Node
  ↓
┌─ Node A ─┐
├─ Node B ─┤ (Parallel Execution)
└─ Node C ─┘
  ↓
Aggregation Node
  ↓
END
```

## Key Concepts

### 1. **Independent Operations**
- Nodes that don't depend on each other's output
- Simultaneous execution for performance
- Separate state field updates

### 2. **State Management**
- Multiple nodes updating different state fields
- Concurrent state modifications
- Avoiding state conflicts

### 3. **Performance Optimization**
- Reduced total execution time
- Better resource utilization
- Parallel API calls and computations

### 4. **Result Aggregation**
- Combining results from parallel nodes
- Summary generation from concurrent calculations
- Final state compilation

## Use Cases Demonstrated

### Cricket Statistics (Parallel Workflow)
- **Strike Rate Calculation**: Independent batting performance metric
- **Boundary Analysis**: Separate calculation for boundary scoring
- **Performance Summary**: Aggregation of all parallel calculations

### Content Generation (LLM Parallel)
- **Multiple Content Types**: Different content generated simultaneously
- **Prompt Variations**: Parallel processing of different prompts
- **Result Compilation**: Combining multiple LLM outputs

## Prerequisites
- Python 3.8+
- LangGraph library
- ChatGroq API access (for LLM tutorial)
- Understanding of basic LangGraph concepts

## Performance Benefits
- **Reduced Latency**: Total execution time = max(individual_times) instead of sum
- **Better Throughput**: More operations per unit time
- **Resource Efficiency**: Better CPU/GPU utilization
- **Scalability**: Easy to add more parallel operations

## Running the Tutorials
1. Set up your environment and API keys
2. Start with the basic parallel workflow
3. Progress to LLM parallel operations
4. Compare execution times with sequential alternatives

## Best Practices
- Ensure operations are truly independent
- Consider resource limits (API rate limits, memory)
- Plan for error handling in parallel operations
- Design proper state field separation

## Next Steps
After mastering parallel workflows, explore:
- Conditional workflows (folder 3)
- Iterative workflows (folder 4)
- Combining parallel and conditional patterns