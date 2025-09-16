# Building ChatBot Tutorial

This folder demonstrates how to build a conversational chatbot using LangGraph with memory and message management capabilities.

## Tutorial Files

### Basic ChatBot (`10. basic_chatbot.ipynb`)

**Concepts Covered:**
- Conversational AI implementation with LangGraph
- Message history management
- Memory persistence using checkpointers
- Interactive chat loop implementation
- Thread-based conversation tracking

**Code References:**
- `ChatState` class: Manages conversation state
  - `messages`: Annotated list of BaseMessage objects using `add_messages`
- `chat()` function: Core conversation node that processes messages
- `MemorySaver()`: In-memory checkpoint storage for conversation persistence
- `add_messages`: LangGraph utility for proper message list management
- Interactive chat loop with `thread_id` for session management

**Key Learning:**
- How to implement persistent conversation memory
- Message list management with LangGraph utilities
- Thread-based conversation tracking
- Interactive chatbot user interface patterns

## Workflow Architecture

### Chat Flow Pattern
```
START
  ↓
chat node (Process messages with LLM)
  ↓
END (with state persistence)
```

### Message Management Flow
```
User Input → HumanMessage → Chat State → LLM Processing → AI Response → Updated State
     ↑                                                                        ↓
     └── Continue Conversation ←── Memory Checkpoint ←── State Persistence ←──┘
```

## Key Concepts

### 1. **Message Management**
- Using `BaseMessage` and `HumanMessage` for structured conversation
- `add_messages` annotation for proper message list handling
- Conversation history preservation

### 2. **State Persistence**
- `MemorySaver` for in-memory conversation storage
- Checkpoint-based state management
- Thread ID for session tracking

### 3. **Interactive Chat Loop**
- Continuous conversation handling
- User input processing
- Real-time response generation

### 4. **Conversational AI Integration**
- ChatGroq LLM integration for responses
- Temperature control for response creativity
- Context-aware conversation handling

## Implementation Details

### State Structure
```python
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
```

### Memory Configuration
```python
checkpoint = MemorySaver()  # In-memory storage
workflow = graph.compile(checkpointer=checkpoint)
```

### Chat Loop Pattern
```python
thread_id = "1"  # Session identifier
while True:
    user_message = input("You: ")
    # Process message through workflow
    # Display AI response
    # Continue conversation
```

## Features Demonstrated

### Conversation Continuity
- Messages persist across interactions
- Context maintained throughout conversation
- Historical context available for responses

### Memory Management
- Automatic message history storage
- Thread-based session separation
- Checkpoint-based state recovery

### User Experience
- Interactive command-line interface
- Real-time response generation
- Continuous conversation flow

## Prerequisites
- Python 3.8+
- LangGraph library
- LangChain Core for message types
- ChatGroq API access
- dotenv for environment management

## Advanced Features

### Thread Management
- Multiple conversation threads support
- Session isolation and management
- Thread-specific conversation history

### Message Types
- Support for different message types (Human, AI, System)
- Structured conversation flow
- Message metadata handling

### Checkpoint System
- Automatic state saving and loading
- Conversation recovery capabilities
- Memory persistence across sessions

## Use Cases
- **Customer Support Bots**: Interactive customer service
- **Educational Assistants**: Learning and Q&A systems
- **Personal Assistants**: Task-oriented conversations
- **Content Creation**: Collaborative writing and brainstorming

## Running the Tutorial
1. Set up your ChatGroq API key in `.env`
2. Install required dependencies
3. Open the Jupyter notebook
4. Execute cells to start the interactive chatbot
5. Type messages and observe conversation flow

## Customization Options
- **Personality**: Modify temperature and prompt patterns
- **Memory Types**: Switch between MemorySaver and other checkpointers
- **Message Processing**: Add custom message handling logic
- **UI Enhancement**: Integrate with web frameworks or messaging platforms

## Best Practices
- Use appropriate thread IDs for session management
- Handle conversation context size limits
- Implement graceful error handling
- Consider conversation cleanup strategies
- Monitor memory usage for long conversations

## Next Steps
After building a basic chatbot, explore:
- Advanced UI integration (folder 7)
- Streaming responses (folder 8)
- Agent-based conversational systems
- Multi-modal conversation handling

---

## Full Code Walkthrough

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

# 1. LLM Configuration
model = ChatGroq(
  model="llama-3.3-70b-versatile",
  temperature=0.5  # Increase for more creativity, decrease for determinism
)

# 2. State Definition
class ChatState(TypedDict):
  messages: Annotated[list[BaseMessage], add_messages]

# 3. Core Chat Node (Pure Logic: accepts state, returns partial diff)
def chat(state: ChatState):
  response = model.invoke(state["messages"])  # Pass full history
  return {"messages": [response]}  # Return list so reducer appends

# 4. Build Graph
graph = StateGraph(ChatState)
graph.add_node("chat", chat)
graph.add_edge(START, "chat")

# 5. Add Checkpointer for Memory
checkpoint = MemorySaver()
workflow = graph.compile(checkpointer=checkpoint)

# 6. Interactive Loop
thread_id = "1"  # Session identifier; change for parallel conversations
while True:
  user_text = input("You: ")
  if user_text.lower() in {"exit", "quit"}: break

  # Supply only the NEW human message; prior messages restored via checkpoint
  state_update = {"messages": [HumanMessage(content=user_text)]}
  config = {"configurable": {"thread_id": thread_id}}

  result = workflow.invoke(state_update, config=config)
  bot_reply = result["messages"][-1].content
  print("Bot:", bot_reply)

# 7. Inspect Final State
final_state = workflow.get_state({"configurable": {"thread_id": thread_id}})
print("History length:", len(final_state.values["messages"]))
```

## Code Explanation
| Section | Purpose | Notes |
|---------|---------|-------|
| Model init | Configures LLM | Temperature tunes creativity vs consistency |
| `ChatState` | Defines state schema | Reducer handles list merging safely |
| `chat` node | Generates AI reply | Returns diff (only new message) |
| Graph build | Registers node + edge | Linear START → chat → END |
| Checkpointer | Persists state per thread | Enables continuity across loop iterations |
| Interactive loop | Collects user input | Supplies only incremental state change |
| State inspection | Post-run debugging | Allows auditing & analytics |

## Why Use `add_messages` Reducer?
Without it you would have to: (1) read existing messages, (2) concatenate new messages manually, (3) return full list every invocation. The reducer abstracts this pattern so each node returns only the delta while LangGraph performs consistent merging.

## Advanced Patterns

### 1. Streaming Responses
You can surface partial tokens to the user interface as they are generated (ideal for latency-sensitive UX):
```python
for event in workflow.stream(state_update, config=config):
  for node_name, node_value in event.items():
    # node_value is the partial state after that node
    last = node_value.get("messages", [])[-1]
    if hasattr(last, 'content'):
      print(last.content, end="|", flush=True)
```
Wrap token buffering logic or UI push updates around this loop.

### 2. Multi-Thread / Multi-User Sessions
```python
def send(thread_id: str, text: str):
  return workflow.invoke(
    {"messages": [HumanMessage(content=text)]},
    config={"configurable": {"thread_id": thread_id}}
  )

send("alice", "Hello!")
send("bob", "Hi there!")
send("alice", "How are you?")  # Maintains Alice history only
```

### 3. Memory Truncation (Simple Token Guard)
```python
def trim_messages(messages, max_msgs=20):
  if len(messages) <= max_msgs: return messages
  # Keep first system message (if any) + last recent interactions
  head = [m for m in messages[:1] if getattr(m, 'type', '') == 'system']
  tail = messages[-(max_msgs- len(head)) :]
  return head + tail

def chat(state: ChatState):
  pruned = trim_messages(state["messages"], max_msgs=24)
  response = model.invoke(pruned)
  return {"messages": [response]}
```

### 4. Adding a System Prompt
Insert persistent instruction once per new thread:
```python
from langchain_core.messages import SystemMessage
def bootstrap(thread_id: str):
  workflow.invoke(
    {"messages": [SystemMessage(content="You are a concise helpful assistant.")]},
    config={"configurable": {"thread_id": thread_id}}
  )
```

### 5. Tool-Augmented Chat (Preview Idea)
Add a decision node before `chat` that inspects the last user message, calls a tool when pattern matches, and injects the tool result as a new message prior to the LLM reply.

## Troubleshooting
| Symptom | Cause | Fix |
|---------|-------|-----|
| ValueError about `thread_id` | Missing configurable key for checkpointer | Pass `config={"configurable": {"thread_id": "..."}}` |
| Repeated responses | Accidentally re-supplying full history each turn | Only pass new `HumanMessage` delta |
| Memory ballooning | Unlimited message growth | Apply trimming / summarization strategy |
| Slow responses | Large context passed each turn | Prune or summarize older turns |
| Inconsistent tone | No system instruction baseline | Add a system message at thread start |

## Extension Ideas
- Summarize older turns into a running summary field.
- Add sentiment classification node logging per turn.
- Integrate a vector store for long-term recall beyond short-term message list.
- Insert moderation filter node before chat generation.
- Provide a WebSocket layer for real-time streaming to a web UI.

## Minimal Summarization Example
```python
class ChatState(TypedDict):
  messages: Annotated[list[BaseMessage], add_messages]
  summary: str

def summarize(messages):
  text = "\n".join(m.content for m in messages[-8:])
  return model.invoke(f"Summarize briefly: {text}").content

def maybe_summarize(state: ChatState):
  if len(state["messages"]) % 10 == 0:  # every 10 turns
    return {"summary": summarize(state["messages"])}
  return {}
```
Add `maybe_summarize` as a node before `chat` and feed `state['summary']` into the prompt template.

## Observability Hooks (Pattern)
Wrap node logic to log latency, token usage, or costs:
```python
import time
def chat(state: ChatState):
  start = time.time()
  response = model.invoke(state["messages"])  # LLM call
  duration = time.time() - start
  print(f"chat node latency: {duration:.2f}s")
  return {"messages": [response]}
```

---

## Summary
This chatbot example shows the minimal viable conversational memory loop in LangGraph. By layering reducers, checkpoints, and optional streaming, you can scale from a toy REPL into a production-ready conversational service with observability, memory shaping, and tool augmentation.