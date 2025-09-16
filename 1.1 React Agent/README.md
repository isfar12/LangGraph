# React Agent Tutorial

This folder demonstrates how to build and use React (Reasoning and Acting) agents using LangGraph with built-in LangChain agent tools.

## Tutorial Files

### Simple React Agent (`simple_react.ipynb`)
**Concepts Covered:**
- Using pre-built LangChain agents
- AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION
- Tool integration (TavilySearch)
- Agent initialization and execution
- Custom tool creation

**Code References:**
- `ChatGroq` model setup with llama-3.3-70b-versatile
- `TavilySearch` tool for web search capabilities
- `initialize_agent()` with structured chat ReAct description
- `create_react_agent()` with custom tools
- Custom tool example: `add_exclamation()` function
- ReAct prompt template from LangChain hub

**Key Learning:**
- How to use pre-built LangChain agents
- Tool integration and configuration
- Agent types and their use cases
- Verbose mode for debugging agent reasoning

**Full Code Walkthrough:**

```python
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain.agents import initialize_agent, AgentType
from dotenv import load_dotenv
load_dotenv()

model = ChatGroq(
	model="llama-3.3-70b-versatile",
	temperature=0.5
)

search_tool = TavilySearch(search_depth="basic")
tools = [search_tool]

agent = initialize_agent(
	tools=tools,
	llm=model,
	agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
	verbose=True,
	return_intermediate_steps=True
)

agent.invoke("What is the weather in Barisal Division?")
```

Explanation:
- `initialize_agent` wraps together: the LLM, tool set, and a ReAct prompt template.
- `STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION` enforces a schema-driven format (Thought → Action → Observation cycles) improving tool reliability.
- `verbose=True` prints the internal reasoning steps for learning/debugging purposes.
- `return_intermediate_steps=True` ensures the tool usage trail is accessible in the response dict.

**Using a Hub ReAct Prompt Manually:**

```python
from langchain import hub
prompt = hub.pull("hwchase17/react")  # canonical ReAct template
print(prompt)  # Inspect the instructions + format placeholders
```

**Adding a Custom Tool:**

```python
from langchain.tools import Tool

def add_exclamation(query: str) -> str:
	return query + "!!!"

custom_tool = Tool(
	name="add_exclamation",
	description="Appends three exclamation marks to the end of the input string",
	func=add_exclamation
)

tools = [search_tool, custom_tool]
```

**Creating a ReAct Agent Programmatically:**

```python
from langchain.agents import create_react_agent, AgentExecutor

react_agent = create_react_agent(llm=model, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=react_agent, tools=tools, verbose=True, return_intermediate_steps=True)

response = executor.invoke({"input": "Find a fact about Jupiter then shout 'giant planet'"})
print(response["output"])            # Final answer
print(response["intermediate_steps"]) # (AgentAction, Observation) tuples
```

Explanation of Flow:
1. The model produces a Thought + decides on a tool = `AgentAction`.
2. Tool is executed → returns an Observation.
3. Observation appended to scratchpad, model reasons again.
4. When it decides it has enough info it returns an `AgentFinish` (final answer + any return metadata).

**Intermediate Steps Structure:**
Each element is `(AgentAction, str_observation)` where:
- `AgentAction.tool` → tool name string.
- `AgentAction.tool_input` → input passed to the tool.
- Observation is the string returned by the tool (may be truncated or summarized by wrappers).

**Common Debug Tips:**
- If the agent keeps choosing the wrong tool: refine the tool's `description`.
- If it hallucinates answers instead of using the tool: lower `temperature` or enforce tool use with prompt edits.
- If tool inputs are malformed: inspect `AgentAction.tool_input` to adjust expected input shape.

**Extending Further:**
- Add a calculator tool for numeric reasoning.
- Add a memory layer to persist past interactions.
- Wrap the executor into a LangGraph node to integrate with broader workflows.

## Prerequisites
- Python 3.8+
- LangGraph and LangChain libraries
- ChatGroq API access
- TavilySearch API access
- dotenv for environment management

## Agent Capabilities
The React agent in this tutorial can:
- Perform web searches using TavilySearch
- Answer questions requiring external knowledge
- Demonstrate reasoning and acting patterns
- Use structured chat format for better tool usage

## Key Concepts
- **ReAct Pattern**: Combines reasoning (thinking) and acting (tool usage)
- **Structured Chat**: Formatted approach to agent-tool interaction
- **Zero-Shot**: Agent works without specific examples
- **Tool Integration**: How agents utilize external tools

## Running the Tutorial
1. Set up your API keys in `.env` file
2. Install required dependencies
3. Open the Jupyter notebook
4. Execute cells to see agent in action
5. Try different queries to understand agent behavior

## Next Steps
Proceed to the Custom React Agent tutorial (folder 1.2) to learn how to build React agents from scratch using LangGraph.