# LangGraph Basic Tutorials

This folder contains fundamental LangGraph tutorials that introduce core concepts and basic workflow patterns.

## Tutorial Files

### 1. Basic Workflow (`1.basic_workflow.ipynb`)
**Concepts Covered:**
- Creating your first LangGraph StateGraph
- Defining TypedDict states (`BMIState`)
- Adding nodes and edges to graphs
- Graph compilation and execution
- Sequential workflow patterns

**Code References:**
- `BMIState` class: Defines state structure with weight, height, and BMI fields
- `calculate_bmi()` function: Node that performs BMI calculation
- `bmi_type()` function: Node that categorizes BMI results
- Graph structure: START → calculate_bmi → bmi_type → END

**Key Learning:**
- How to structure state using TypedDict
- Basic node-to-node sequential flow
- Graph compilation with `workflow.compile()`

**Full Code Walkthrough:**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class BMIState(TypedDict):
	weight: float
	height: float
	bmi: float  # will be added by the node

def calculate_bmi(state: BMIState) -> BMIState:
	state["bmi"] = state["weight"] / (state["height"] ** 2)
	return state  # returning updated state (in-place mutation pattern used in early examples)

graph = StateGraph(BMIState)
graph.add_node("calculate_bmi", calculate_bmi)
graph.add_edge(START, "calculate_bmi")
graph.add_edge("calculate_bmi", END)
workflow = graph.compile()
final_state = workflow.invoke({"weight": 70, "height": 1.75})
print(final_state)
```

Explanation:
- `BMIState` defines the shape of the state the workflow will carry between nodes.
- `calculate_bmi` reads from required fields (`weight`, `height`) and writes a new field (`bmi`).
- `StateGraph(BMIState)` constrains what keys live in the state (type-safety & clarity).
- `add_node` registers a computational step; `add_edge` wires execution order.
- `compile()` produces an executable `workflow` object.
- `invoke(initial_state)` executes the graph once (synchronously) and returns the final state dict.

Improved second version adds a classification node:

```python
def bmi_type(state: BMIState) -> BMIState:
	bmi = state["bmi"]
	if bmi < 18.5:
		state["bmi_type"] = "Underweight"
	elif bmi < 24.9:
		state["bmi_type"] = "Normal weight"
	elif bmi < 29.9:
		state["bmi_type"] = "Overweight"
	else:
		state["bmi_type"] = "Obesity"
	return state

graph = StateGraph(BMIState)
graph.add_node("calculate_bmi", calculate_bmi)
graph.add_node("bmi_type", bmi_type)
graph.add_edge(START, "calculate_bmi")
graph.add_edge("calculate_bmi", "bmi_type")
graph.add_edge("bmi_type", END)
workflow = graph.compile()
```

Takeaways:
- Adding another node just means registering it and extending edges.
- Explicit edges make control flow auditable & visualizable.
- Each node can choose to mutate in-place or return partial updates; returning dict diffs (immutable style) is generally preferred for more complex graphs.

### 2. LLM Workflow (`2.llm_workflow.ipynb`)
**Concepts Covered:**
- Integrating Large Language Models with LangGraph
- ChatGroq LLM integration
- Environment variable management with dotenv
- Simple question-answering workflows

**Code References:**
- `LLMState` class: Contains question and answer fields
- `llm_qna()` function: Node that processes questions using LLM
- ChatGroq model configuration with temperature settings
- Prompt engineering for Q&A tasks

**Key Learning:**
- How to incorporate LLMs into LangGraph workflows
- State management for conversational patterns
- LLM model configuration and prompt handling

**Full Code Walkthrough:**

```python
from dotenv import load_dotenv
load_dotenv()
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.7)

class LLMState(TypedDict):
	question: str
	answer: str  # populated by the node

def llm_qna(state: LLMState) -> LLMState:
	prompt = f"Answer the following question: {state['question']}"
	# `.invoke` returns a message-like object; `.content` contains the text
	state["answer"] = llm.invoke(prompt).content
	return state

graph = StateGraph(LLMState)
graph.add_node("llm_qna", llm_qna)
graph.add_edge(START, "llm_qna")
graph.add_edge("llm_qna", END)
workflow = graph.compile()
final_state = workflow.invoke({"question": "What is the capital of France?"})
print(final_state["answer"])  # "Paris" (expected)
```

Explanation:
- `load_dotenv()` loads credentials (e.g. GROQ API key) required by `ChatGroq`.
- The state is minimal: just an input (`question`) and an output (`answer`).
- A single node both constructs the prompt and records the result.
- The model call is synchronous (`invoke`). For concurrent or streaming usage you can later adopt `ainvoke` or `stream` patterns.

Extension Ideas:
- Add a `followup` node that generates a related next question.
- Add error handling: catch API failures and set an `error` field.
- Cache answers for repeated questions (state-level or external cache).

### 3. Prompt Chaining (`3.prompt_chaining.ipynb`)
**Concepts Covered:**
- Sequential prompt processing
- Multi-step content generation
- Dependency between workflow nodes
- Blog content creation pipeline

**Code References:**
- `BlogState` class: Manages title, outline, and content
- `create_outline()` function: Generates blog outline from title
- `create_blog()` function: Creates detailed content from outline
- Chained workflow: outline generation → content creation

**Key Learning:**
- How to chain multiple LLM calls in sequence
- State passing between dependent operations
- Building complex content generation pipelines

**Full Code Walkthrough:**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_groq import ChatGroq

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)

class BlogState(TypedDict):
	title: str
	outline: str  # created by first node
	content: str  # created by second node

def create_outline(state: BlogState) -> BlogState:
	prompt = f"Generate an outline for a blog on the topic - {state['title']}"
	state["outline"] = model.invoke(prompt).content
	return state

def create_blog(state: BlogState) -> BlogState:
	prompt = (
		f"Generate a detailed blog post based on the title {state['title']} and outline: {state['outline']}"
	)
	state["content"] = model.invoke(prompt).content
	return state

graph = StateGraph(BlogState)
graph.add_node("create_outline", create_outline)
graph.add_node("create_blog", create_blog)
graph.add_edge(START, "create_outline")
graph.add_edge("create_outline", "create_blog")
graph.add_edge("create_blog", END)
workflow = graph.compile()
final_state = workflow.invoke({"title": "Benefits of Functional Programming"})
print(final_state["content"][:300])
```

Explanation:
- Two dependent LLM calls: the second strictly requires the first's output.
- Same shared state object flows through both nodes — no manual passing needed.
- Natural pattern for multi-stage generation (outline → draft → polish → summary).

Refactoring Tip (Immutable Updates):
Instead of mutating the state, you can return only changed keys:

```python
def create_outline(state: BlogState):
	prompt = f"Generate an outline for a blog on the topic - {state['title']}"
	return {"outline": model.invoke(prompt).content}
```

LangGraph will merge the returned diff with existing state values, reducing side effects.

## Prerequisites
- Python 3.8+
- LangGraph library
- ChatGroq API access
- dotenv for environment management

## Running the Tutorials
1. Ensure all dependencies are installed
2. Set up your `.env` file with necessary API keys
3. Open Jupyter notebooks in sequence
4. Execute cells step by step to understand the concepts

## Next Steps
After completing these basic tutorials, proceed to:
- React Agent implementations (folders 1.1 and 1.2)
- Parallel workflows (folder 2)
- Conditional workflows (folder 3)