# Reflexion Agent

This folder contains an implementation of the Reflexion agent pattern, which enables agents to learn from their mistakes through self-reflection and iterative improvement.

## Files Overview

### `chains.py`
**Purpose:** Implementation of reflexion-based agent chains and workflows
**Code References:**
- Reflexion agent implementation using LangGraph
- Self-reflection and learning mechanisms
- Iterative improvement through failure analysis
- Memory and experience integration

## Reflexion Agent Concept

### Core Philosophy
Reflexion agents learn from their failures by:
1. **Executing tasks** and observing outcomes
2. **Reflecting on failures** to understand what went wrong
3. **Updating their approach** based on reflection insights
4. **Applying learned knowledge** to future similar tasks

### Learning Cycle
```
Task Execution → Outcome Evaluation → Failure Analysis → Reflection → Knowledge Update → Improved Performance
     ↑                                                                                            ↓
     └── Apply Learned Knowledge ← Memory Integration ← Experience Storage ← Learning Synthesis ←┘
```

## Key Concepts

### 1. **Reflexive Learning**
- Learning from both successes and failures
- Self-analysis and critique capabilities
- Adaptive behavior based on experience

### 2. **Memory Integration**
- Long-term experience storage
- Pattern recognition from past failures
- Knowledge accumulation and refinement

### 3. **Iterative Improvement**
- Continuous learning and adaptation
- Performance improvement over time
- Self-correcting behavior patterns

### 4. **Failure Analysis**
- Systematic analysis of unsuccessful attempts
- Root cause identification
- Learning extraction from mistakes

## Architecture Overview

### Reflexion Workflow
```
New Task
    ↓
Retrieve Relevant Experience
    ↓
Execute Task with Current Knowledge
    ↓
Evaluate Outcome
    ↓
[Success] → Store Positive Experience
[Failure] → Reflect on Failure → Update Knowledge → Retry
```

### Learning Integration
```
Experience Memory ← Reflection Insights ← Failure Analysis ← Task Outcome
     ↓                      ↓                    ↓              ↓
Knowledge Base → Strategy Updates → Improved Execution → Better Results
```

## Implementation Features

### Self-Reflection Mechanism
- Automatic failure analysis
- Insight generation from mistakes
- Learning pattern recognition

### Experience Management
- Long-term memory for experiences
- Pattern matching for similar situations
- Knowledge retrieval and application

### Adaptive Execution
- Strategy modification based on learning
- Dynamic approach adjustment
- Continuous improvement process

## Use Cases

### Problem-Solving Tasks
- **Code Generation**: Learning from compilation errors and test failures
- **Mathematical Problem Solving**: Improving through incorrect solution analysis
- **Research Tasks**: Enhancing information gathering through iteration

### Interactive Systems
- **Game Playing**: Learning from losing strategies
- **Conversation Agents**: Improving through conversation feedback
- **Creative Tasks**: Enhancing output quality through critique cycles

### Automation Tasks
- **Process Optimization**: Learning from inefficient executions
- **Quality Control**: Improving accuracy through error analysis
- **Decision Making**: Enhancing choices through outcome evaluation

## Prerequisites
- Python 3.8+
- LangGraph library
- Understanding of agent architectures
- Memory management systems
- Evaluation and feedback mechanisms

## Key Advantages

### Continuous Learning
- Persistent improvement over time
- Accumulation of domain knowledge
- Adaptive behavior development

### Failure Tolerance
- Learning opportunities from mistakes
- Resilient performance improvement
- Self-correcting capabilities

### Experience Utilization
- Leveraging past experiences for current tasks
- Pattern recognition and application
- Knowledge transfer across similar problems

## Implementation Patterns

### Reflexion Loop
```python
def reflexion_cycle(task, max_iterations=3):
    for iteration in range(max_iterations):
        result = execute_task(task)
        if is_successful(result):
            store_success_experience(task, result)
            return result
        else:
            reflection = reflect_on_failure(task, result)
            update_knowledge(reflection)
            task = modify_approach(task, reflection)
    return final_result
```

### Experience Integration
```python
class ReflexionAgent:
    def __init__(self):
        self.memory = ExperienceMemory()
        self.knowledge_base = KnowledgeBase()
    
    def execute_with_learning(self, task):
        relevant_experience = self.memory.retrieve(task)
        approach = self.knowledge_base.get_strategy(task, relevant_experience)
        result = execute_task(task, approach)
        self.learn_from_outcome(task, approach, result)
        return result
```

### Learning Integration
```python
def learn_from_failure(task, failure_result):
    reflection = analyze_failure(failure_result)
    insights = extract_insights(reflection)
    update_strategy(task_type, insights)
    store_experience(task, failure_result, reflection, insights)
```

## Advanced Features

### Multi-Domain Learning
- Cross-domain knowledge transfer
- General learning principles application
- Adaptive learning strategies

### Collaborative Reflexion
- Shared experience across agent instances
- Collective learning from distributed failures
- Community knowledge building

### Meta-Learning
- Learning how to learn more effectively
- Reflection strategy optimization
- Adaptive reflection mechanisms

## Performance Optimization

### Memory Efficiency
- Selective experience storage
- Relevant experience retrieval
- Memory consolidation strategies

### Learning Speed
- Rapid insight extraction
- Efficient knowledge application
- Accelerated improvement cycles

### Generalization
- Pattern recognition across tasks
- Knowledge transfer capabilities
- Adaptive strategy development

## Evaluation Metrics

### Learning Progress
- Performance improvement over time
- Failure rate reduction
- Knowledge accumulation measurement

### Adaptation Capability
- Response to new challenges
- Transfer learning effectiveness
- Strategy modification success

### Reflection Quality
- Insight accuracy and relevance
- Learning extraction effectiveness
- Knowledge application success

## Best Practices

### Reflection Design
- Structured failure analysis
- Comprehensive insight extraction
- Actionable learning generation

### Memory Management
- Efficient experience storage
- Relevant knowledge retrieval
- Memory optimization strategies

### Learning Balance
- Balance between exploration and exploitation
- Appropriate learning rate adjustment
- Overfitting prevention

---

## Full Code Walkthrough

### Core Chain (`chains.py`)
```python
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.output_parsers import PydanticToolsParser
from pydantic import BaseModel, Field

class Reflection(BaseModel):
    missing: str = Field(..., description="Critique what informations are missing")
    superfluous: str = Field(..., description="Critique what informations are superfluous")

class Answer(BaseModel):
    answer: str = Field(..., description="The answer to the user's question")
    reflection: Reflection = Field(..., description="Reflection on the provided answer")

answer_parser = PydanticToolsParser(tools=[Answer])
model = ChatGroq(model="openai/gpt-oss-20b", temperature=0)

template = """You are a highly intelligent question answering bot.\nYou will be provided with a question, and a set of context information.\nYou will first answer the question based on the context information.\nThen, you will reflect on your answer and critique what informations are missing\nand what informations are superfluous.  \nFinally, you will provide your final answer and your reflection in a json format.\nUse the following format:\n{{\n"answer": "your answer",\n"reflection": {{\n"missing": "what is missing",\n"superfluous": "what is superfluous"\n}}\n}}\nUse the following context information to answer the question:\n{context}\nQuestion: {question}\nAnswer:"""

prompt = PromptTemplate(input_variables=["context", "question"], template=template)
chain = prompt | model.bind_tools(tools=[Answer], tool_choice="Answer") | answer_parser

response = chain.invoke({
    "context": "The capital of France is Paris. The capital of Germany is Berlin.",
    "question": "What are the capitals of France and Germany?"
})
print(response)
```

### Explanation Table
| Component | Purpose | Notes |
|-----------|---------|-------|
| `Answer` schema | Structured output | Enforces presence of answer + reflection |
| `PydanticToolsParser` | Parses tool output | Converts tool call to pydantic instance |
| `bind_tools(... tool_choice="Answer")` | Forces schema selection | Reduces ambiguity |
| Temperature=0 | Determinism | Facilitates reproducible reflections |
| Unified prompt | Multi-phase instruction | Answer → critique pattern |

## Adding Iterative Reflexion
Wrap answer generation in a loop capturing improved responses.
```python
def improve(question, context, max_iters=3):
    prior = None
    for i in range(max_iters):
        base_context = context
        if prior:
            base_context += f"\nPrevious answer: {prior.answer}\nPrevious critique missing: {prior.reflection.missing}\nPrevious critique superfluous: {prior.reflection.superfluous}"
        result = chain.invoke({"context": base_context, "question": question})
        if not prior:
            prior = result
            continue
        # Stop if critique indicates nothing missing
        if result.reflection.missing.strip().lower() in {"", "none", "nothing"}:
            return result
        prior = result
    return prior
```

## Storing Experience (Conceptual)
```python
from dataclasses import dataclass
@dataclass
class Experience:
    question: str
    context: str
    answer: str
    missing: str
    superfluous: str

experience_log: list[Experience] = []

def log(result, question, context):
    experience_log.append(Experience(
        question=question,
        context=context,
        answer=result.answer,
        missing=result.reflection.missing,
        superfluous=result.reflection.superfluous
    ))
```

## Retrieval-Augmented Reflexion
Before answering, retrieve prior experiences with similar questions and inject summaries into the context, reducing repeated omissions.

## Failure Mode Diagnostics
| Symptom | Cause | Remedy |
|---------|-------|--------|
| Reflection repeats same missing items | Loop not incorporating previous critique | Inject prior critique into prompt |
| Missing field blank often | Prompt too weak for critique | Strengthen critique instruction / examples |
| Superfluous always empty | Model ignoring second field | Provide explicit JSON exemplar |

## Prompt Hardening Example
Add: "If nothing is missing, set missing to explicit string 'None'. If nothing is superfluous, set superfluous to 'None'." Ensures disambiguation between failure and genuine completeness.

## Graph Extension (LangGraph Pattern)
Nodes:
1. `draft` (initial answer & reflection)
2. `decision` (stop or refine?)
3. `augment` (retrieve experiences)
4. `refine` (new answer with previous critique)

Conditional edges route `decision -> END` or `decision -> augment -> refine -> decision`.

## Evaluation Metrics (Operational)
Track across iterations:
- Tokens used vs improvement delta
- Distinct missing items resolved
- Average reflection length

## Summary
The Reflexion agent combines structured answer generation with enforced self-critique. Iterative loops plus experience logging raise answer quality over time, while deterministic settings make progress measurable and regressions detectable.

## Integration Considerations

### Computational Resources
- Memory requirements for experience storage
- Processing overhead for reflection
- Learning cycle optimization

### Feedback Systems
- Quality evaluation mechanisms
- Performance monitoring systems
- Learning effectiveness measurement

### Scalability
- Multi-agent learning coordination
- Distributed experience sharing
- Scalable knowledge management

## Future Directions

### Enhanced Reflection
- More sophisticated failure analysis
- Deeper insight generation
- Advanced learning mechanisms

### Integration Opportunities
- Combination with other agent architectures
- Multi-modal learning capabilities
- Real-world application integration

This Reflexion agent implementation provides a foundation for building self-improving AI systems that learn continuously from their experiences and failures.