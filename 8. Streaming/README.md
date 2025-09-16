# Streaming Tutorial

This folder demonstrates how to implement streaming responses in LangGraph workflows, enabling real-time output generation and improved user experience.

## Tutorial Files

### Streaming Chat (`12. streaming_chat.ipynb`)

**Concepts Covered:**
- Real-time streaming responses from LLM workflows
- Asynchronous output generation
- Progressive content delivery
- Enhanced user experience with immediate feedback

**Code References:**
- Streaming workflow implementation using LangGraph
- Real-time response generation patterns
- Async/await patterns for streaming
- Integration with streaming-capable LLMs

**Key Learning:**
- How to implement streaming in LangGraph workflows
- Real-time response generation and delivery
- User experience improvements through streaming
- Handling asynchronous workflow execution

---

## Minimal Streaming Workflow Example
```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.4)

def chat(state: ChatState):
    # Assume model supports streaming tokens internally (pseudo pattern)
    response = model.invoke(state["messages"])  # For real streaming use provider's stream interface
    return {"messages": [response]}

graph = StateGraph(ChatState)
graph.add_node("chat", chat)
graph.add_edge(START, "chat")
workflow = graph.compile()

update = {"messages": [HumanMessage(content="Explain quantum tunneling simply.")]}
for event in workflow.stream(update):
    # event = {"chat": {"messages": [...]} }
    node_state = event.get("chat")
    if not node_state: continue
    latest = node_state["messages"][-1]
    print(latest.content)
```

### Explanation
| Component | Purpose |
|-----------|---------|
| `workflow.stream(update)` | Yields state deltas per node execution | 
| `event` dict | Maps node name → partial state | 
| Content access | Extract new AI message tokens or final message | 

## Distinguishing Node Streaming vs Token Streaming
LangGraph's `workflow.stream(...)` streams at the granularity of node completions (state diffs). Token-level streaming requires an LLM provider that emits incremental tokens. Combine both for best UX: provider token callback → accumulate into message → yield partial state.

### Token Assembly Pattern (Conceptual)
```python
def chat(state: ChatState):
    buffer = []
    for token in model.stream(state["messages"]):  # hypothetical .stream()
        buffer.append(token)
        partial = "".join(buffer)
        yield {"messages": [AIMessage(content=partial)]}  # generator-style node
    # Final yield happens automatically with full content
```
If your framework doesn't allow generator nodes, accumulate tokens externally and periodically emit interim UI updates while returning only the final message to the graph.

## Async Streaming Usage
```python
async def run():
    update = {"messages": [HumanMessage(content="Give me a haiku about oceans")]}
    async for event in workflow.astream(update):
        if "chat" in event:
            msg = event["chat"]["messages"][-1]
            print(msg.content)
```

## Merging Streaming With UI (Streamlit Sketch)
```python
import streamlit as st
from langchain_core.messages import HumanMessage

placeholder = st.empty()
accum = ""
for event in workflow.stream({"messages": [HumanMessage(content=user_input)]}):
    node = event.get("chat")
    if not node: continue
    content = node["messages"][-1].content
    accum = content  # replace or append depending on semantics
    placeholder.markdown(accum)
```

## Hybrid: Periodic Partial Flushes
When provider exposes token callbacks, push partial text every N tokens to reduce UI churn while retaining responsiveness.

| Strategy | Flush Frequency | Pros | Cons |
|----------|-----------------|------|------|
| Every token | 1 | Fastest feedback | High overhead, flicker |
| Batch of 5 | 5 | Balanced smoothness | Slight delay |
| Time-sliced | 100ms | Stable cadence | Complexity |

## Backpressure & Flow Control
In high-load scenarios throttle streaming updates to protect UI and network. Insert an async sleep, token counter gate, or coalesce updates.

## Error Handling in Streaming
```python
try:
    for event in workflow.stream(update):
        process(event)
except Exception as e:
    # Provide partial context & fallback
    log_error(e)
    show_partial_response()
```

## Pattern: Multi-Node Streaming
Parallel nodes can each emit their completion events; interleave them: sort by arrival time or group by node for UI sections.

## Example: Parallel Idea Streaming (Conceptual)
```python
class IdeaState(TypedDict):
    topic: str
    ideas: list[str]

def idea_gen(state: IdeaState):
    # imagine streaming partial list
    for i in range(3):
        yield {"ideas": [f"Idea {i} about {state['topic']}"]}

# Graph node with generator semantics (conceptual API)
```

## Observability Hooks
Track latency to first token vs total latency; expose metrics dashboard for tuning temperature / max tokens.

## Fallback Strategy
If streaming unsupported or fails mid-response:
1. Detect missing provider capability → switch to `.invoke()`.
2. If connection drops mid-stream → finalize with best-effort partial content + note.

## Security Considerations
| Risk | Vector | Mitigation |
|------|--------|------------|
| Token leakage | Logging raw stream | Scrub logs / redact |
| Prompt injection mid-stream | Malicious user input | Sanitize / moderate input upfront |
| Resource exhaustion | Infinite open streams | Enforce timeout & max tokens |

## Summary
Streaming elevates perceived performance by surfacing incremental progress. Combine node-level streaming with provider token callbacks, implement sensible throttling, and always provide robust fallback paths for reliability.

## Workflow Architecture

### Streaming Flow Pattern
```
User Input
    ↓
Workflow Start
    ↓
LLM Processing (Streaming)
    ↓
Real-time Token Generation
    ↓
Progressive Response Display
    ↓
Complete Response
```

### Streaming vs Batch Processing
```
Batch:     Input → [Process] → Complete Output
Streaming: Input → Process → Token → Token → Token → Complete
```

## Key Concepts

### 1. **Real-time Response Generation**
- Progressive token generation and display
- Immediate user feedback
- Reduced perceived latency

### 2. **Streaming Protocols**
- Token-by-token output generation
- Chunk-based response streaming
- Real-time data transmission

### 3. **Asynchronous Processing**
- Non-blocking workflow execution
- Concurrent processing capabilities
- Responsive user interfaces

### 4. **User Experience Enhancement**
- Immediate visual feedback
- Reduced waiting time perception
- Interactive response generation

## Implementation Patterns

### Basic Streaming Setup
```python
# Streaming workflow configuration
workflow = graph.compile()
for chunk in workflow.stream(input_data):
    # Process each streaming chunk
    yield chunk
```

### Async Streaming Pattern
```python
async def stream_response(input_data):
    async for chunk in workflow.astream(input_data):
        # Handle streaming chunks asynchronously
        yield chunk
```

### Token-level Streaming
```python
# Token-by-token response handling
for token in llm_stream(prompt):
    # Display each token as it arrives
    display_token(token)
```

## Features Demonstrated

### Progressive Response Display
- Token-by-token text generation
- Real-time UI updates
- Smooth user experience

### Streaming Integration
- LLM streaming capabilities
- Workflow-level streaming support
- Frontend streaming integration

### Performance Optimization
- Reduced time-to-first-token
- Better resource utilization
- Enhanced responsiveness

## Streaming Benefits

### User Experience
- **Immediate Feedback**: Users see responses start immediately
- **Reduced Waiting**: Perception of faster response times
- **Interactive Feel**: More engaging conversation experience

### Technical Advantages
- **Resource Efficiency**: Better memory and processing utilization
- **Scalability**: Handle more concurrent users
- **Responsiveness**: Non-blocking operation

### Business Impact
- **User Engagement**: Higher user satisfaction and retention
- **Performance Perception**: Faster application feel
- **Competitive Advantage**: Modern, responsive user experience

## Prerequisites
- Python 3.8+
- LangGraph library with streaming support
- Streaming-capable LLM provider
- Understanding of async/await patterns
- Basic knowledge of web streaming protocols

## Implementation Considerations

### LLM Provider Support
- Ensure your LLM provider supports streaming
- Configure appropriate streaming parameters
- Handle streaming errors and interruptions

### Frontend Integration
- WebSocket or Server-Sent Events for real-time updates
- Progressive UI updates
- Proper error handling for streaming failures

### Network Considerations
- Handle network interruptions gracefully
- Implement retry mechanisms
- Consider bandwidth limitations

## Advanced Streaming Features

### Structured Streaming
- Stream different types of content (text, data, metadata)
- Multi-modal streaming support
- Structured response formatting

### Conditional Streaming
- Stream different content based on conditions
- Adaptive streaming based on user preferences
- Context-aware streaming behavior

### Parallel Streaming
- Multiple concurrent streaming operations
- Aggregated streaming responses
- Complex streaming workflows

## Use Cases
- **Interactive Chatbots**: Real-time conversation interfaces
- **Content Generation**: Progressive article or code generation
- **Data Processing**: Real-time analysis and reporting
- **Educational Tools**: Interactive tutoring and explanation systems

## Performance Optimization

### Streaming Configuration
- Optimal chunk sizes for your use case
- Buffer management for smooth delivery
- Connection pooling for efficiency

### Error Handling
- Graceful degradation for streaming failures
- Retry mechanisms for interrupted streams
- Fallback to batch processing when needed

### Monitoring
- Stream performance metrics
- User experience analytics
- Error rate monitoring

## Integration Patterns

### Web Application Integration
```javascript
// Frontend streaming integration
const eventSource = new EventSource('/stream-endpoint');
eventSource.onmessage = function(event) {
    displayStreamingResponse(event.data);
};
```

### Real-time UI Updates
```python
# Backend streaming endpoint
@app.route('/stream')
def stream():
    def generate():
        for chunk in workflow.stream(input_data):
            yield f"data: {chunk}\n\n"
    return Response(generate(), mimetype='text/plain')
```

## Best Practices
- Implement proper error handling for streaming interruptions
- Use appropriate chunk sizes for your network conditions
- Provide fallback options for non-streaming scenarios
- Monitor streaming performance and user experience
- Consider mobile and low-bandwidth users

## Testing Strategies
- Test streaming under various network conditions
- Verify proper error handling and recovery
- Load test streaming endpoints
- User experience testing for streaming interactions

## Next Steps
After mastering streaming, explore:
- Advanced streaming protocols (WebRTC, WebSocket)
- Multi-modal streaming (text, audio, video)
- Distributed streaming architectures
- Real-time collaboration features
- Integration with reflection agents (folder 9)