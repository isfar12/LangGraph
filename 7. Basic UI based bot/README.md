# Basic UI-Based Bot

This folder demonstrates how to create a web-based user interface for LangGraph chatbots using Streamlit as the frontend and LangGraph as the backend service.

## Files Overview

### Backend Implementation (`langgraph_backend.py`)

**Purpose:** Core chatbot logic and workflow implementation
**Code References:**
- `ChatState` class: Message state management using `add_messages`
- `chatnode()`: Core conversation processing function
- `InMemorySaver()`: Checkpoint-based memory management
- LangGraph workflow compilation with persistence
- ChatGroq LLM integration for conversation handling

**Key Components:**
- StateGraph setup for conversation flow
- Message annotation for proper list handling
- Checkpointer integration for conversation memory
- Model configuration with temperature control

### Frontend Implementation (`streamlit_frontend.py`)

**Purpose:** Web-based user interface for chatbot interaction
**Code References:**
- Streamlit UI components for chat interface
- Session state management for conversation history
- Integration with LangGraph backend service
- Real-time message display and input handling

## Architecture Overview

### System Design
```
User Browser (Streamlit UI)
        ↓
Streamlit Frontend
        ↓
HTTP/Function Calls
        ↓
LangGraph Backend
        ↓
LLM Provider (ChatGroq)
```

### Component Interaction
```
Frontend (UI) ↔ Backend (Logic) ↔ LLM (Intelligence)
     ↓              ↓                    ↓
Session State   Workflow State      Context Memory
```

## Key Concepts

### 1. **Separation of Concerns**
- Frontend: User interface and experience
- Backend: Business logic and workflow management
- Clear API boundaries between components

### 2. **State Management**
- Frontend session state for UI persistence
- Backend workflow state for conversation memory
- Synchronized state across components

### 3. **Real-time Interaction**
- Live chat interface with immediate responses
- Streaming or batch response handling
- Interactive user experience

### 4. **Memory Integration**
- Persistent conversation history
- Context-aware responses
- Session management across UI interactions

## Backend Features

### Conversation Management
- Message history preservation using checkpoints
- Thread-based conversation isolation
- Automatic state persistence

### LLM Integration
- ChatGroq model integration
- Configurable response parameters
- Context-aware conversation handling

### Workflow Design
- Simple START → chat → END flow
- State management with message annotations
- Checkpoint-based persistence

## Frontend Features

### User Interface
- Clean, intuitive chat interface
- Real-time message display
- Input handling and validation

### Session Management
- Browser session state persistence
- Conversation history display
- Multi-session support capability

### Integration Layer
- Backend service communication
- Error handling and user feedback
- Responsive user experience

## Prerequisites
- Python 3.8+
- LangGraph library
- Streamlit framework
- ChatGroq API access
- dotenv for environment management

## Running the Application

### Backend Setup
1. Configure environment variables in `.env`
2. Install required dependencies
3. Ensure LangGraph backend is properly configured

### Frontend Launch
1. Install Streamlit: `pip install streamlit`
2. Run the frontend: `streamlit run streamlit_frontend.py`
3. Access the web interface in your browser

### Integration Testing
1. Start both backend and frontend components
2. Test conversation flow through web interface
3. Verify state persistence across sessions

## Development Workflow

### Backend Development
```python
# langgraph_backend.py structure
- Import dependencies
- Configure LLM and checkpointer
- Define ChatState and chat function
- Create and compile workflow
- Export workflow for frontend use
```

### Frontend Development
```python
# streamlit_frontend.py structure
- Import Streamlit and backend
- Configure page layout
- Manage session state
- Handle user input
- Display conversation history
```

## Customization Options

### UI Customization
- Streamlit theme configuration
- Custom CSS styling
- Component layout modifications
- Responsive design improvements

### Backend Extensions
- Additional workflow nodes
- Custom memory backends
- Enhanced conversation logic
- Multi-model LLM support

### Integration Enhancements
- WebSocket communication
- Real-time streaming responses
- Authentication and user management
- Multi-tenant conversation support

## Use Cases
- **Customer Support Interfaces**: Web-based customer service bots
- **Educational Platforms**: Interactive learning assistants
- **Internal Tools**: Employee-facing AI assistants
- **Prototype Development**: Rapid chatbot prototyping and testing

## Architecture Benefits
- **Scalability**: Separate frontend and backend scaling
- **Maintainability**: Clear separation of concerns
- **Flexibility**: Easy UI/UX modifications without backend changes
- **Reusability**: Backend can support multiple frontend types

## Best Practices
- Keep frontend and backend loosely coupled
- Use proper error handling across components
- Implement proper session management
- Consider security for production deployments
- Plan for horizontal scaling of backend services

## Advanced Features
- **Multi-user Support**: User authentication and isolation
- **Conversation Analytics**: Usage tracking and insights
- **Custom Themes**: Branded user interface design
- **Mobile Responsiveness**: Cross-device compatibility

## Deployment Considerations
- **Backend Hosting**: Cloud functions, containers, or servers
- **Frontend Hosting**: Streamlit Cloud, Heroku, or custom hosting
- **Environment Management**: Production vs development configurations
- **Monitoring**: Application performance and error tracking

## Next Steps
After building a basic UI-based bot, explore:
- Advanced Streamlit features and components
- WebSocket integration for real-time communication
- Authentication and user management systems
- Production deployment strategies
- Integration with streaming responses (folder 8)

---

## Full Backend Code Walkthrough
```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)

class ChatState(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]

def chatnode(state: ChatState):
        response = model.invoke(state["messages"])
        return {"messages": [response]}

checkpointer = InMemorySaver()
graph = StateGraph(ChatState)
graph.add_node("chatnode", chatnode)
graph.add_edge(START, "chatnode")
graph.add_edge("chatnode", END)
chatbot = graph.compile(checkpointer=checkpointer)
```

### Explanation
| Element | Role | Notes |
|---------|------|-------|
| `ChatState` | State schema | Single field with reducer for message accumulation |
| `chatnode` | Conversational turn | Returns diff (list of new AI message) |
| `InMemorySaver` | Checkpoints | Thread-safe ephemeral memory |
| Graph edges | Flow control | Linear flow, end after node executes |
| `chatbot` | Compiled app | Exposed to UI layer |

## Full Frontend Code Walkthrough
```python
import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {"configurable": {"thread_id": "thread_1"}}

if "message_history" not in st.session_state:
        st.session_state["message_history"] = []

# Display prior messages
for m in st.session_state["message_history"]:
        with st.chat_message(m["role"]):
                st.markdown(m["content"])

user_input = st.chat_input("Ask Anything")
if user_input:
        st.session_state["message_history"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
                st.markdown(user_input)

        result = chatbot.invoke({"messages": [HumanMessage(content=user_input)]}, config=CONFIG)
        ai_text = result["messages"][-1].content
        st.session_state["message_history"].append({"role": "assistant", "content": ai_text})
        with st.chat_message("assistant"):
                st.markdown(ai_text)
```

### Explanation
| Feature | Purpose | Detail |
|---------|---------|--------|
| Session state | UI persistence | Survives reruns for a single browser tab |
| `chat_input` | User capture | Triggers rerun on submit |
| `chat_message` | Structured display | Roles differentiate styling |
| Backend invoke | Core interaction | Supplies only latest human message |
| Thread id | Backend continuity | Isolates conversation memory |

## Streaming Upgrade Pattern (Conceptual)
```python
placeholder = st.empty()
accum = ""
for event in chatbot.stream({"messages": [HumanMessage(content=user_input)]}, config=CONFIG):
        # event shape: {"chatnode": {"messages": [...partial or final...]}}
        node_state = event.get("chatnode")
        if not node_state: continue
        msg = node_state["messages"][-1]
        text = getattr(msg, 'content', '')
        accum = text  # or append partial chunks if model supports token streaming
        placeholder.markdown(accum)
```

## Adding System Prompt Initialization
```python
from langchain_core.messages import SystemMessage
def ensure_system(thread_id: str):
        st.session_state.setdefault("system_init", set())
        if thread_id in st.session_state["system_init"]: return
        chatbot.invoke({"messages": [SystemMessage(content="You are a concise helpful assistant.")]},
                                   config={"configurable": {"thread_id": thread_id}})
        st.session_state["system_init"].add(thread_id)
```

## Multi-User / Multi-Thread Strategy
| Approach | Pros | Cons |
|----------|------|------|
| Single thread id | Simplicity | Shared history collision |
| User id as thread id | Isolation | Need auth layer |
| Compound key (user + channel) | Fine-grained separation | More management complexity |

## Memory Trimming Pattern
```python
MAX_MESSAGES = 30
def prune():
        msgs = st.session_state["message_history"]
        if len(msgs) > MAX_MESSAGES:
                # Keep initial system or first few plus tail
                head = msgs[:2]
                tail = msgs[-(MAX_MESSAGES - len(head)) :]
                st.session_state["message_history"] = head + tail
```

## Error Handling Wrapper
```python
def safe_invoke(payload, config):
        try:
                return chatbot.invoke(payload, config=config)
        except Exception as e:
                st.error(f"Invocation failed: {e}")
                raise
```

## Deployment Tips
| Concern | Recommendation |
|---------|----------------|
| Secrets | Use Streamlit secrets or env vars |
| Cold start | Preload model at module import |
| Scaling | Frontend + backend behind reverse proxy |
| Observability | Add logging & request IDs |
| Latency | Enable streaming, trim context |

## Extension Ideas
- Add a tool selection sidebar (toggle knowledge base lookup).
- Persist conversation transcripts to a database.
- Add per-user analytics (turn count, average latency).
- Integrate authentication (e.g. OAuth) for user-specific histories.
- Introduce presence indicators for multi-user rooms.

## Security Considerations
| Risk | Mitigation |
|------|------------|
| Prompt injection | Sanitize or constrain tool invocation layer |
| Data leakage | Scope histories per authenticated user |
| Resource abuse | Rate limit per IP / user |
| Sensitive logs | Scrub PII before logging |

## Summary
This UI-backed bot illustrates clean separation between the LangGraph conversational core and a lightweight Streamlit interface. By layering streaming, memory shaping, and multi-thread strategies you can evolve this into a production-grade conversational application.