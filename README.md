# LangGraph Tutorial Collection

A comprehensive collection of LangGraph tutorials and examples demonstrating various workflow patterns, agent architectures, and advanced AI system implementations.

## 🎯 Overview

This repository contains hands-on tutorials and implementations showcasing the power and flexibility of LangGraph for building AI workflows, agents, and applications. From basic concepts to advanced agent architectures, these tutorials provide practical examples and reusable code patterns.

## 📚 Tutorial Structure

### Foundation Concepts

#### [1. Basic Workflows](1.%20Basic/)
- **Basic Workflow**: StateGraph fundamentals, BMI calculator with sequential nodes
- **LLM Workflow**: ChatGroq integration, question-answering patterns
- **Prompt Chaining**: Multi-step content generation, blog creation pipeline

#### [2. Parallel Workflows](2.%20Parallel%20Workflow/)
- **Parallel Execution**: Concurrent node processing, cricket statistics calculation
- **LLM Parallel Operations**: Multiple simultaneous AI operations, performance optimization

#### [3. Conditional Workflows](3.%20Conditional%20Workflow/)
- **Mathematical Branching**: Quadratic equation solver with discriminant-based routing
- **LLM Conditional Logic**: AI-powered decision making and content routing

#### [4. Iterative Workflows](4.%20Iterative%20Workflows/)
- **Loop Implementation**: Safe iteration patterns, step counting, termination conditions
- **LLM Iterative Improvement**: Content refinement through AI-driven iteration

### Agent Implementations

#### [1.1 React Agent](1.1%20React%20Agent/)
- **Pre-built Agents**: LangChain AgentExecutor usage, TavilySearch integration
- **Tool Integration**: Custom tool creation, structured chat patterns

#### [1.2 Custom React Agent](1.2%20Custom%20React%20Agent/)
- **Manual Implementation**: Custom ReAct agent from scratch using LangGraph
- **Tool Execution**: Alternative to ToolExecutor, manual tool lookup and execution
- **State Management**: ReactAgentState, intermediate steps tracking

### Application Development

#### [5. Building ChatBot](5.%20Building%20ChatBot/)
- **Conversational AI**: Memory-enabled chatbots, message management
- **Persistence**: Conversation history, thread-based session management

#### [6. Persistence](6.%20Persistence/)
- **State Management**: Checkpoint-based persistence, InMemorySaver usage
- **Workflow Recovery**: State restoration, session continuation

#### [7. Basic UI Based Bot](7.%20Basic%20UI%20based%20bot/)
- **Web Interface**: Streamlit frontend with LangGraph backend
- **System Architecture**: Frontend-backend separation, real-time interaction

#### [8. Streaming](8.%20Streaming/)
- **Real-time Responses**: Token-by-token streaming, progressive content delivery
- **User Experience**: Immediate feedback, reduced perceived latency

### Advanced Agent Systems

#### [9. Reflection Agent System](9.%20Reflection%20Agent%20System/)
- **Self-Critique**: Automated answer evaluation and improvement
- **Research Integration**: Query generation, information gathering, content enhancement
- **Structured Output**: Pydantic schemas for consistent AI responses

#### [10. Reflexion Agent](10.%20Reflexion%20Agent/)
- **Learning from Failures**: Self-improvement through mistake analysis
- **Experience Memory**: Long-term learning, pattern recognition
- **Adaptive Behavior**: Continuous improvement and strategy modification

## 🔧 Technical Stack

### Core Technologies
- **LangGraph**: Workflow orchestration and state management
- **LangChain**: LLM integration and tool management
- **ChatGroq**: Primary LLM provider (llama-3.3-70b-versatile)
- **Python 3.8+**: Core programming language

### Supporting Libraries
- **Pydantic**: Data validation and structured outputs
- **Streamlit**: Web UI framework
- **TavilySearch**: Web search capabilities
- **dotenv**: Environment variable management

### Development Tools
- **Jupyter Notebooks**: Interactive development and tutorials
- **Type Hints**: TypedDict for state management
- **Async/Await**: Streaming and concurrent operations

## 🚀 Getting Started

### Prerequisites
```bash
# Install core dependencies
pip install langgraph langchain langchain-groq
pip install python-dotenv pydantic streamlit
pip install tavily-python  # For search capabilities
```

### Environment Setup
Create a `.env` file with your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Quick Start
1. **Begin with basics**: Start with `1. Basic/` folder tutorials
2. **Explore patterns**: Progress through workflow patterns (parallel, conditional, iterative)
3. **Build agents**: Implement React agents and custom architectures
4. **Create applications**: Build chatbots and web interfaces
5. **Advanced systems**: Explore reflection and reflexion agents

## 📊 Tutorial Progression

### Beginner Path
1. Basic Workflows → LLM Integration → Prompt Chaining
2. Simple React Agent → Tool Integration
3. Basic ChatBot → Persistence

### Intermediate Path
1. Parallel Workflows → Conditional Logic → Iterative Patterns
2. Custom React Agent → Advanced Tool Management
3. UI-based Applications → Streaming Implementation

### Advanced Path
1. Reflection Agent System → Self-Critique Mechanisms
2. Reflexion Agent → Learning from Failures
3. Complex Multi-Agent Systems

## 🎯 Key Learning Outcomes

### Foundational Skills
- **State Management**: TypedDict, state transitions, persistence
- **Workflow Design**: Node creation, edge configuration, conditional routing
- **LLM Integration**: Model configuration, prompt engineering, response handling

### Advanced Capabilities
- **Agent Architecture**: ReAct patterns, tool integration, custom implementations
- **System Design**: Frontend-backend separation, streaming, real-time interfaces
- **AI Enhancement**: Self-reflection, iterative improvement, learning systems

### Production Readiness
- **Error Handling**: Graceful failures, retry mechanisms, validation
- **Performance**: Parallel processing, streaming, optimization strategies
- **Scalability**: State management, memory efficiency, concurrent operations

## 🔍 Code Patterns and Best Practices

### State Management
```python
class ExampleState(TypedDict):
    input: str
    output: str
    metadata: dict
```

### Node Implementation
```python
def process_node(state: ExampleState) -> dict:
    # Process state and return updates
    return {"output": processed_result}
```

### Conditional Routing
```python
def route_decision(state: ExampleState) -> Literal["path_a", "path_b"]:
    return "path_a" if condition else "path_b"
```

### Tool Integration
```python
@tool
def custom_tool(query: str) -> str:
    """Custom tool implementation"""
    return process_query(query)
```

## 🏗️ Architecture Patterns

### Sequential Workflow
- Linear processing with dependent steps
- Simple state transitions
- Clear data flow

### Parallel Processing
- Concurrent independent operations
- Performance optimization
- Resource efficiency

### Conditional Branching
- Dynamic path selection
- Business logic implementation
- Multi-scenario handling

### Iterative Improvement
- Loop-based processing
- Quality-driven iteration
- Progressive enhancement

### Agent-Based Systems
- Autonomous decision making
- Tool usage and integration
- Complex reasoning patterns

## 🎨 Use Cases and Applications

### Business Applications
- **Customer Support**: AI-powered help desks and chatbots
- **Content Creation**: Automated writing and editing systems
- **Data Analysis**: Intelligent data processing and reporting
- **Decision Support**: AI-assisted business decision making

### Educational Systems
- **Tutoring Platforms**: Adaptive learning and personalized instruction
- **Research Assistance**: Information gathering and synthesis
- **Knowledge Management**: Intelligent content organization and retrieval

### Development Tools
- **Code Generation**: AI-powered development assistance
- **Testing Automation**: Intelligent test case generation and execution
- **Documentation**: Automated technical writing and maintenance

## 🔄 Continuous Learning Path

### Weekly Learning Schedule
- **Week 1**: Basic concepts and simple workflows
- **Week 2**: Agent implementations and tool integration
- **Week 3**: Application development and UI integration
- **Week 4**: Advanced patterns and production considerations

### Practice Projects
1. **Personal Assistant**: Implement a multi-functional AI assistant
2. **Content Pipeline**: Build an automated content creation system
3. **Knowledge Base**: Create an intelligent Q&A system
4. **Business Automation**: Develop workflow automation tools

## 🤝 Contributing

### Adding New Tutorials
1. Follow the established folder structure
2. Include comprehensive README.md files
3. Provide working code examples
4. Document prerequisites and setup steps

### Code Standards
- Use type hints and TypedDict for state management
- Include proper error handling
- Follow naming conventions
- Add inline documentation

## 📄 License

This tutorial collection is provided for educational purposes. Individual libraries and APIs may have their own licensing terms.

## 🆘 Support and Resources

### Documentation
- [LangGraph Official Documentation](https://python.langchain.com/docs/langgraph)
- [LangChain Documentation](https://python.langchain.com/)
- [ChatGroq API Documentation](https://console.groq.com/docs)

### Community
- GitHub Issues for bug reports and questions
- Community discussions and best practices
- Tutorial suggestions and improvements

---

**Start your LangGraph journey today!** Begin with the [Basic Workflows](1.%20Basic/) and progress through increasingly sophisticated AI system implementations.
---

## 🔀 Quick Navigation (By Goal)
| Goal | Start Here | Then Explore | Advanced |
|------|------------|--------------|----------|
| Learn basics | 1. Basic | 2. Parallel / 3. Conditional | 4. Iterative |
| Build an agent fast | 1.1 React Agent | 1.2 Custom React | 9. Reflection |
| Stateful chat | 5. Building ChatBot | 6. Persistence | 7. UI Bot + 8. Streaming |
| Improve answers | 9. Reflection | 10. Reflexion | Multi-agent (future) |
| Production UX | 7. UI Bot | 8. Streaming | Observability & persistence patterns |

## 🔗 Cross-Linked Highlights
- Loop & refinement pattern: [Iterative Workflows](4.%20Iterative%20Workflows/)
- Streaming nuances: [Streaming](8.%20Streaming/) (node vs token streaming)
- Self-critique vs experiential learning: [Reflection](9.%20Reflection%20Agent%20System/) vs [Reflexion](10.%20Reflexion%20Agent/)
- Checkpoint reuse for chat memory: [Persistence](6.%20Persistence/)
- Frontend/backend separation: [Basic UI Based Bot](7.%20Basic%20UI%20based%20bot/)

## 🧭 Concept Index
| Concept | Folder | Notes |
|---------|--------|-------|
| Sequential Workflow | 1. Basic | Foundations |
| Parallel Branches | 2. Parallel Workflow | Performance pattern |
| Conditional Routing | 3. Conditional Workflow | Logic branching |
| Iteration / Loop | 4. Iterative Workflows | Termination guards |
| Conversational Memory | 5. Building ChatBot | Reducer + checkpoint |
| Persistence | 6. Persistence | State history |
| UI Integration | 7. Basic UI Based Bot | Session vs workflow state |
| Streaming | 8. Streaming | Node vs token streaming |
| Reflection | 9. Reflection Agent System | Structured critique |
| Reflexion | 10. Reflexion Agent | Failure-driven learning |

## ⚙️ Additional Patterns
- Diff-style state updates (return only changed keys)
- List reducers (`Annotated[list[T], add_messages]`) for accumulation
- Evaluation vs mutation separation (LLM improvement loops)
- Structured output enforcement (Pydantic / tool binding)
- Dual termination guards (max steps + quality threshold)

## 🧪 One-Line Examples
```python
# Minimal compile & invoke
workflow = (StateGraph(ExampleState)
    .add_node("step", process_node)
    .add_edge(START, "step")
    .compile())
workflow.invoke({"input": "Hi"})
```
```python
# Stream state deltas
for event in workflow.stream({"input": "Hi"}):
    print(event)
```
```python
# Conditional edges
graph.add_conditional_edges("evaluate", route_decision, {"path_a": node_a, "path_b": node_b})
```
```python
# Structured output
structured = model.with_structured_output(MySchema)
structured.invoke("Prompt")
```
```python
# Iterative refinement skeleton
for i in range(max_iters):
    decision = evaluate(state)
    if decision.get("approved") == "yes":
        break
    delta = improve(state)
    state = {**state, **delta}
```

## 🔍 State Inspection
```python
state = workflow.get_state(config)
history = list(workflow.get_state_history(config=config))
```

---