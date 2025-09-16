# Conditional Workflow Tutorials

This folder demonstrates conditional logic and routing in LangGraph workflows, showing how to build decision-making systems that branch based on state conditions.

## Tutorial Files

### 1. Conditional Workflow (`6.conditional_workflow.ipynb`)
**Concepts Covered:**
- Conditional routing using `add_conditional_edges()`
- Decision-making based on state values
- Multiple execution paths from routing logic
- Mathematical problem solving with branching

**Code References:**
- `QuadState` class: State for quadratic equation solving
- `get_equation()`: Formats the quadratic equation
- `get_discriminant()`: Calculates discriminant value
- `route_node()`: Conditional routing function with Literal return type
- Branch nodes: `two_real_roots()`, `one_real_root()`, `no_real_roots()`
- Routing logic based on discriminant value

**Key Learning:**
- How to implement conditional routing in workflows
- Using `Literal` types for routing decisions
- Mathematical branching based on calculated values
- Multiple execution paths from a single decision point

**Full Code Walkthrough (Quadratic Discriminant Example):**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

class QuadState(TypedDict):
  a: int
  b: int
  c: int
  equation: str
  discriminant: float
  result: str

def get_equation(state: QuadState):
  return {"equation": f"{state['a']}x^2 + {state['b']}x + {state['c']} = 0"}

def get_discriminant(state: QuadState):
  return {"discriminant": state['b']**2 - 4*state['a']*state['c']}

def two_real_roots(state: QuadState):
  return {"result": "Two real roots"}

def one_real_root(state: QuadState):
  return {"result": "One real root"}

def no_real_roots(state: QuadState):
  return {"result": "No real roots"}

def route_node(state: QuadState) -> Literal['two_real_roots','one_real_root','no_real_roots']:
  d = state['discriminant']
  if d > 0:
    return 'two_real_roots'
  elif d == 0:
    return 'one_real_root'
  else:
    return 'no_real_roots'

graph = StateGraph(QuadState)
graph.add_node("get_equation", get_equation)
graph.add_node("get_discriminant", get_discriminant)
graph.add_node("two_real_roots", two_real_roots)
graph.add_node("one_real_root", one_real_root)
graph.add_node("no_real_roots", no_real_roots)

graph.add_edge(START, "get_equation")
graph.add_edge("get_equation", "get_discriminant")
graph.add_conditional_edges(
  "get_discriminant",
  route_node,
  {
    'two_real_roots': 'two_real_roots',
    'one_real_root': 'one_real_root',
    'no_real_roots': 'no_real_roots'
  }
)
graph.add_edge("two_real_roots", END)
graph.add_edge("one_real_root", END)
graph.add_edge("no_real_roots", END)

workflow = graph.compile()
final_state = workflow.invoke({"a": 1, "b": 2, "c": 1})
print(final_state["equation"], final_state["result"])
```

Explanation:
- Each node returns only changed keys → safer than mutating the entire state.
- `route_node` returns a literal label *matching* keys in the mapping passed to `add_conditional_edges`.
- Divergent nodes terminate by routing directly to `END` (simple fan-out then converge to termination pattern).
- You can add more branches without changing prior logic—modify only the routing dictionary & add nodes.

Error Prevention Tips:
- Always cover all routing possibilities; otherwise a missing mapping raises an error.
- Use `Literal[...]` for route return type to get editor/type checker hints if a branch string is mistyped.
- Avoid side effects (mutation) inside route functions: limit them to pure decisions.

### 2. Conditional Workflow with LLM (`7.conditional_workflow_llm.ipynb`)
**Concepts Covered:**
- LLM-based conditional routing
- Content moderation and filtering
- Dynamic workflow paths based on AI decisions
- Combining LLM intelligence with workflow control

**Code References:**
- LLM-powered routing decisions
- Content analysis and classification
- Dynamic path selection based on AI output
- ChatGroq integration for decision making

**Key Learning:**
- How to use LLMs for workflow routing decisions
- AI-powered content classification and filtering
- Dynamic workflow adaptation based on content analysis
- Combining human logic with AI decision-making

**Illustrative LLM-Based Routing Pattern:**

```python
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

class ModerationState(TypedDict):
  text: str
  classification: str
  action: str
  explanation: str

def classify(state: ModerationState):
  prompt = f"Classify the following text as SAFE or UNSAFE, output just one word. Text: {state['text']}"
  label = model.invoke(prompt).content.strip().upper()
  if label not in {"SAFE", "UNSAFE"}:
    label = "SAFE"  # fallback
  return {"classification": label}

def route(state: ModerationState) -> Literal['allow','block']:
  return 'allow' if state['classification'] == 'SAFE' else 'block'

def allow_content(state: ModerationState):
  return {"action": "CONTENT_ALLOWED", "explanation": "Text passed safety checks."}

def block_content(state: ModerationState):
  # Optional extra explanation step
  prompt = f"Explain briefly why this text may be unsafe: {state['text']}"
  reason = model.invoke(prompt).content
  return {"action": "CONTENT_BLOCKED", "explanation": reason}

graph = StateGraph(ModerationState)
graph.add_node("classify", classify)
graph.add_node("allow_content", allow_content)
graph.add_node("block_content", block_content)
graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", route, {"allow": "allow_content", "block": "block_content"})
graph.add_edge("allow_content", END)
graph.add_edge("block_content", END)
workflow = graph.compile()

print(workflow.invoke({"text": "I will send you a gift tomorrow!"}))
```

Discussion:
- The classification step is intentionally constrained: one-word output keeps parsing trivial.
- A second prompt in the blocking path gives user-friendly justification.
- Temperature = 0 reduces variance—important for routing determinism.

Hardening Ideas:
- Add a regex or enum post-processor for `classification`.
- Introduce a confidence score threshold (second model call or heuristic) before blocking.
- Log borderline cases to a review queue (append to a list in state with `Annotated[..., operator.add]`).

## Workflow Architecture

### Conditional Routing Pattern
```
START
  ↓
Initial Processing
  ↓
Decision Node (route_node)
  ↓
┌─ Condition A → Path A ─┐
├─ Condition B → Path B ─┤
└─ Condition C → Path C ─┘
  ↓
END
```

## Key Concepts

### 1. **Conditional Routing**
- `add_conditional_edges()` for dynamic path selection
- Routing functions that return `Literal` types
- State-based decision making

### 2. **Mathematical Branching**
- Discriminant-based quadratic equation solving
- Numerical condition evaluation
- Mathematical logic implementation

### 3. **LLM-Powered Decisions**
- AI-based content analysis and routing
- Natural language understanding for decisions
- Dynamic workflow adaptation

### 4. **Multiple Execution Paths**
- Different processing based on conditions
- Specialized handling for different scenarios
- Conditional result generation

## Quadratic Equation Solver Example

### Decision Logic
- **Discriminant > 0**: Two real roots path
- **Discriminant = 0**: One real root path  
- **Discriminant < 0**: No real roots path

### State Flow
1. Input coefficients (a, b, c)
2. Format equation string
3. Calculate discriminant
4. Route based on discriminant value
5. Execute appropriate solution path

## LLM Conditional Examples

### Content Moderation
- Analyze text content for appropriateness
- Route to approval or rejection paths
- Dynamic handling based on content analysis

### Classification Routing
- Categorize input content
- Route to specialized processing nodes
- AI-powered decision making

## Prerequisites
- Python 3.8+
- LangGraph library
- Understanding of basic LangGraph patterns
- ChatGroq API access (for LLM tutorial)
- Basic mathematical concepts (for quadratic solver)

## Design Patterns

### Routing Function Structure
```python
def route_node(state: StateType) -> Literal['path1', 'path2', 'path3']:
    if condition1:
        return 'path1'
    elif condition2:
        return 'path2'
    else:
        return 'path3'
```

### Conditional Edge Setup
```python
graph.add_conditional_edges(
    "decision_node",
    route_node,
    {
        "path1": "node_a",
        "path2": "node_b", 
        "path3": "node_c"
    }
)
```

## Running the Tutorials
1. Start with the mathematical conditional workflow
2. Understand routing logic and decision points
3. Progress to LLM-based conditional routing
4. Experiment with different conditions and paths

## Use Cases
- **Mathematical Problem Solving**: Route based on numerical conditions
- **Content Processing**: Different handling for different content types
- **Business Logic**: Implement complex decision trees
- **Error Handling**: Route based on error conditions or validation results

## Best Practices
- Keep routing logic simple and clear
- Use descriptive path names
- Handle all possible conditions
- Consider default/fallback paths
- Test all conditional branches

## Next Steps
Explore combining conditional patterns with:
- Iterative workflows (folder 4)
- Parallel processing within conditional branches
- Complex multi-decision workflows