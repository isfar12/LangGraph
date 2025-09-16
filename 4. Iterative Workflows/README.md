# Iterative Workflow Tutorials

This folder demonstrates iterative and looping patterns in LangGraph workflows, showing how to build systems that repeat operations until certain conditions are met.

## Tutorial Files

### 1. Iterative Workflow (`8. Iterative_workflow.ipynb`)
**Concepts Covered:**
- Loop implementation using conditional routing
- Step counting and iteration limits
- Incremental state modifications
- Termination conditions and exit strategies

**Code References:**
- `IterativeState` class: Tracks iteration progress and limits
  - `current_step`: Current iteration counter
  - `max_steps`: Maximum allowed iterations
  - `approved`: Loop termination flag
- `get_length()`: Calculates current input length
- `evaluate()`: Checks termination conditions
- `route_next_step()`: Conditional routing for loop control
- `increase_size()`: Modifies state and increments step counter
- Loop structure: evaluate → route → (continue loop | exit)

**Key Learning:**
- How to implement loops in LangGraph workflows
- Safe iteration with maximum step limits
- State modification patterns in loops
- Conditional loop termination

**Full Code Walkthrough:**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

class IterativeState(TypedDict):
  input: str
  length: int
  output: str
  approved: Literal["yes","no"]
  current_step: int
  max_steps: int

def get_length(state: IterativeState):
  return {"length": len(state["input"])}

def evaluate(state: IterativeState):
  if state["length"] < 10 and state["current_step"] < state["max_steps"]:
    return {"approved": "no"}
  return {"approved": "yes"}

def route_next_step(state: IterativeState) -> Literal["increase_size","within_limit"]:
  return "increase_size" if state["approved"] == "no" else "within_limit"

def increase_size(state: IterativeState):
  new_input = state["input"] + "*"
  return {
    "input": new_input,
    "current_step": state["current_step"] + 1,
    "length": len(new_input)
  }

graph = StateGraph(IterativeState)
graph.add_node("get_length", get_length)
graph.add_node("evaluate", evaluate)
graph.add_node("increase_size", increase_size)
graph.add_edge(START, "get_length")
graph.add_edge("get_length", "evaluate")
graph.add_conditional_edges("evaluate", route_next_step, {"increase_size": "increase_size", "within_limit": END})
graph.add_edge("increase_size", "evaluate")
workflow = graph.compile()

initial = {"input": "HELLO", "length": 0, "output": "", "approved": "no", "current_step": 0, "max_steps": 5}
print(workflow.invoke(initial))
```

Explanation:
- Loop emerges through conditional routing + back edge.
- Dual stopping criteria prevents infinite loops.
- Returns are diff-style (only changed keys) for clarity.
- Routing function is pure (side-effect free) => easier to test.

Enhancements:
- Track history: add `history: Annotated[list[str], operator.add]` and return `{"history": [state['input']]}` in `increase_size`.
- Add early exit pattern: if input contains a sentinel substring.
- Enforce maximum runtime by counting wall-clock seconds externally.

### 2. Iterative Workflow with LLM (`9. Iterative_workflow_llm.ipynb`)
**Concepts Covered:**
- LLM-powered iterative content improvement
- Multi-step content refinement
- AI-driven quality assessment
- Iterative content generation workflows

**Code References:**
- LLM integration for content improvement
- Quality assessment using AI
- Iterative refinement patterns
- Content evaluation and enhancement loops

**Key Learning:**
- How to use LLMs in iterative improvement workflows
- AI-powered quality assessment and refinement
- Multi-step content enhancement patterns
- Balancing automation with quality control

**Illustrative LLM Refinement Loop:**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
from langchain_groq import ChatGroq
import operator
from typing import Annotated

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)

class ImproveState(TypedDict):
  draft: str
  score: int
  decision: Literal["improve","accept"]
  iteration: int
  max_iterations: int
  drafts: Annotated[list[str], operator.add]  # history accumulator

def score_quality(state: ImproveState):
  prompt = f"Score (1-10) clarity+conciseness ONLY number: {state['draft']}"
  raw = model.invoke(prompt).content.strip()
  try:
    score = int(raw.split()[0])
  except ValueError:
    score = 5
  return {"score": score}

def decide(state: ImproveState):
  if state["score"] >= 8 or state["iteration"] >= state["max_iterations"]:
    return {"decision": "accept"}
  return {"decision": "improve"}

def route(state: ImproveState) -> Literal["improve","accept"]:
  return state["decision"]

def improve(state: ImproveState):
  prompt = f"Improve clarity, keep tone: {state['draft']}"
  better = model.invoke(prompt).content
  return {
    "draft": better,
    "iteration": state["iteration"] + 1,
    "drafts": [better]
  }

graph = StateGraph(ImproveState)
graph.add_node("score_quality", score_quality)
graph.add_node("decide", decide)
graph.add_node("improve", improve)
graph.add_edge(START, "score_quality")
graph.add_edge("score_quality", "decide")
graph.add_conditional_edges("decide", route, {"improve": "improve", "accept": END})
graph.add_edge("improve", "score_quality")
workflow = graph.compile()

initial = {"draft": "This sentence might be clearer.", "score": 0, "decision": "improve", "iteration": 0, "max_iterations": 4, "drafts": []}
print(workflow.invoke(initial))
```

Discussion:
- Historical drafts retained via annotated list reducer.
- Pure separation: scoring vs decision vs mutation.
- Determinism improved by low temperature scoring prompt.

Further Ideas:
- Add a `best_draft` field updated only when score improves.
- Add a branch for "regression" if new draft scores worse → revert.
- Introduce multi-criteria scoring (readability, style, accuracy) with parallel scoring nodes.

## Workflow Architecture

### Basic Iterative Pattern
```
START
  ↓
get_length
  ↓
evaluate (check conditions)
  ↓
route_next_step
  ↓
├─ approved="yes" → END
└─ approved="no" → increase_size → back to evaluate
```

### Loop Control Flow
```
Processing Node
     ↓
Evaluation Node
     ↓
Conditional Router
     ↓
├─ Continue → Modification Node → back to Evaluation
└─ Terminate → END
```

## Key Concepts

### 1. **Loop Implementation**
- Using conditional edges for loop control
- State-based iteration decisions
- Safe termination with step limits

### 2. **State Evolution**
- Incremental state modifications
- Step counter management
- Progress tracking through iterations

### 3. **Termination Conditions**
- Multiple exit conditions (quality threshold + step limit)
- Preventing infinite loops
- Graceful termination handling

### 4. **Iterative Improvement**
- Gradual enhancement of content/data
- Quality-driven iteration
- Convergence toward desired outcomes

## String Length Example (Basic Iterative)

### Process Flow
1. **Input**: Initial string (e.g., "HELLO")
2. **Length Check**: Calculate current length
3. **Evaluation**: Check if length < 10 AND steps < max_steps
4. **Decision**: 
   - If needs improvement: add "*" and increment step
   - If satisfactory: terminate workflow
5. **Repeat**: Continue until conditions met

### State Management
```python
# Safe step increment pattern
new_step = state["current_step"] + 1
return {"current_step": new_step, "input": new_input}
```

## LLM Iterative Improvement

### Content Refinement Process
1. **Initial Content**: Starting content or query
2. **Quality Assessment**: LLM evaluates current quality
3. **Improvement Decision**: Determine if refinement needed
4. **Content Enhancement**: LLM improves the content
5. **Repeat**: Continue until quality threshold met

### Quality-Driven Iteration
- AI-powered content evaluation
- Iterative enhancement based on feedback
- Balancing quality with efficiency

## Prerequisites
- Python 3.8+
- LangGraph library
- Understanding of conditional workflows
- ChatGroq API access (for LLM tutorial)
- Basic understanding of loop concepts

## Design Patterns

### Safe Iteration Pattern
```python
def evaluate(state: IterativeState):
    # Always include step limit check
    if condition and state["current_step"] < state["max_steps"]:
        return {"approved": "no"}
    else:
        return {"approved": "yes"}
```

### Step Increment Pattern
```python
def modification_node(state: IterativeState):
    new_step = state["current_step"] + 1
    # Perform modifications
    return {"current_step": new_step, "other_field": new_value}
```

## Common Use Cases
- **Content Improvement**: Iterative refinement of text, code, or data
- **Quality Assurance**: Repeated validation and enhancement
- **Data Processing**: Incremental data transformation
- **Optimization Problems**: Iterative improvement toward optimal solutions
- **Training Workflows**: Multi-step learning and adaptation

## Error Prevention
- **Maximum Step Limits**: Prevent infinite loops
- **State Validation**: Ensure proper state updates
- **Termination Conditions**: Multiple exit strategies
- **Progress Monitoring**: Track iteration progress

## Performance Considerations
- **Convergence Speed**: Balance quality with efficiency
- **Resource Management**: Monitor API calls and processing time
- **Early Termination**: Exit when good enough results achieved
- **Progress Tracking**: Monitor improvement trends

## Running the Tutorials
1. Start with the basic string length example
2. Understand loop control mechanisms
3. Progress to LLM-powered iterative workflows
4. Experiment with different termination conditions

## Best Practices
- Always include maximum iteration limits
- Use clear termination conditions
- Monitor state changes for debugging
- Consider early termination for efficiency
- Test edge cases and boundary conditions

## Next Steps
Combine iterative patterns with:
- Parallel processing within iterations
- Conditional branching in loops
- Agent-based iterative workflows
- Complex multi-objective optimization