# Reflection Agent System

This folder demonstrates advanced agent architectures that incorporate self-reflection and iterative improvement capabilities, allowing agents to critique and enhance their own outputs.

## Files Overview

### Core Implementation Files

#### `schema.py`
**Purpose:** Defines data structures for reflection-based workflows
**Code References:**
- `Reflection` class: Pydantic model for critique structure
  - `missing`: Field for identifying missing information
  - `superfluous`: Optional field for identifying unnecessary content
- `AnswerQuestion` class: Structured response model
  - `answer`: Main response content (~250 words)
  - `search_queries`: List of 1-3 research queries for improvements
  - `reflection`: Embedded reflection and critique
- Pydantic Field descriptions for structured AI responses

#### `chains.py`
**Purpose:** Implements the reflection workflow logic and LLM chains
**Code References:**
- Reflection chain implementation for self-critique
- Research query generation for improvement
- Answer refinement based on reflection feedback
- Integration of reflection loops with LLM responses

## Architecture Overview

### Reflection Workflow Pattern
```
Initial Query
    ↓
Generate Answer
    ↓
Self-Reflection & Critique
    ↓
Generate Research Queries
    ↓
Gather Additional Information
    ↓
Improve Answer
    ↓
Final Response (or iterate)
```

### Self-Improvement Loop
```
Answer Generation → Reflection → Research → Enhancement → Evaluation
     ↑                                                         ↓
     └── Continue Improvement ← Quality Check ← Updated Answer ←┘
```

## Key Concepts

### 1. **Self-Reflection**
- Agent critiques its own outputs
- Identifies missing or superfluous information
- Structured self-evaluation using defined schemas

### 2. **Iterative Improvement**
- Multiple rounds of answer enhancement
- Research-driven improvement process
- Quality-based iteration termination

### 3. **Structured Output**
- Pydantic models for consistent response format
- Field descriptions guiding AI response structure
- Type-safe data handling

### 4. **Research-Driven Enhancement**
- Automatic generation of research queries
- Information gathering for answer improvement
- Evidence-based answer refinement

## Implementation Details

### Reflection Schema Structure
```python
class Reflection(BaseModel):
    missing: str = Field(description="Critique of what is missing")
    superfluous: Optional[str] = None  # Optional critique of excess content
```

### Answer Structure
```python
class AnswerQuestion(BaseModel):
    answer: str = Field(description="The answer to the users question in ~250 words")
    search_queries: List[str] = Field(description="1-3 search queries for researching improvements")
    reflection: Reflection = Field(description="Reflection and critique of the initial answer")
```

### Workflow Components
- **Answer Generation**: Initial response creation
- **Self-Reflection**: Critique and analysis of generated content
- **Research Query Generation**: Identifying information gaps
- **Information Gathering**: External research based on queries
- **Answer Refinement**: Improvement based on reflection and research

---

## Full Code Walkthrough

### Schema (`schema.py`)
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Reflection(BaseModel):
    missing: str = Field(description="Critique of what is missing")
    superfluous: Optional[str] = None

class AnswerQuestion(BaseModel):
    answer: str = Field(description="The answer to the users question in ~250 words")
    search_queries: List[str] = Field(description="1-3 search queries seperately for researching improvements")
    reflection: Reflection = Field(description="Reflection and critique of the initial answer")
```

### Chain (`chains.py`)
```python
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
import datetime
from schema import AnswerQuestion
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.5)
structured_model = model.with_structured_output(AnswerQuestion)

actor_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are an expert AI researcher\n\nCurrent date: {current_date}\n\n1. {first_instruction}\n2. Reflect and critique your answer. Be severe to maximize your improvement.\n3. After the reflection, **list  1-3 search queries seperately** for researching improvements.\nDo not inlcude them inside reflection"""),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Answer the users question above using the required format.")
]).partial(
    current_date=datetime.datetime.now().strftime("%Y-%m-%d"),
    first_instruction="Answer the users question in ~250 words"
)

chain = actor_prompt_template | structured_model

result = chain.invoke({
    "messages": [HumanMessage(content="Explain the theory of relativity in simple terms.")]
})
print(result)
```

### Explanation
| Element | Purpose | Notes |
|---------|---------|-------|
| `with_structured_output` | Enforces schema | Reduces parsing errors |
| `MessagesPlaceholder` | Inserts prior conversation | Enables iterative refinement |
| System instructions | Multi-step guidance | Enumerated to bias structure |
| `partial(...)` | Inject dynamic values | Date + variable first instruction |
| `chain` pipeline | Prompt → model → pydantic | Functional composition |

## Turning This Into an Iterative Improving Agent
Add a loop: generate → reflect → research → refine until quality threshold.

```python
def needs_another_pass(answer: AnswerQuestion):
    # Simple heuristic: if 'missing' field length exceeds threshold
    return len(answer.reflection.missing.split()) > 12 and len(answer.search_queries) > 0

current = chain.invoke({"messages": [HumanMessage(content=question)]})
history = [current]
for i in range(3):  # max 3 refinement rounds
    if not needs_another_pass(current):
        break
    # (Placeholder) gather info using search queries
    notes = "".join(f"Result summary for: {q}\n" for q in current.search_queries)
    refinement_prompt = f"Improve prior answer using these notes:\n{notes}\nOriginal: {current.answer}"
    current = chain.invoke({"messages": [HumanMessage(content=refinement_prompt)]})
    history.append(current)
```

## Integrating a Research Tool (Conceptual)
```python
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Return brief synthesized web results"""
    # Integrate Tavily/Bing/etc. Here placeholder.
    return f"(search results for {query})"
```
Then call `web_search` for each generated query before refining.

## Reflection Quality Heuristics
| Signal | Interpretation | Action |
|--------|---------------|--------|
| Empty `missing` | Answer likely comprehensive | Stop loop |
| Many vague queries | Weak reflection specificity | Tighten prompt guidance |
| Repeated identical queries | Stagnation | Add diversity penalty |

## Prompt Hardening Tips
| Problem | Tweak |
|---------|-------|
| Search queries embedded in reflection text | Add: "List queries each on its own line AFTER reflection section." |
| Overly long answers | Reinforce word limit & penalize excess | 
| Missing reflection fields | Add explicit JSON example & failure instruction |

## Adding JSON Guardrail
If hallucinations occur, wrap model with a JSON schema validator or use `retry_with_fallback` pattern to re-ask on validation failure.

## Potential Graph Conversion (LangGraph)
Nodes:
1. `draft_answer`
2. `reflect`
3. `decide_continue` (conditional)
4. `research` (parallel over queries)
5. `refine`

Conditional edges route either back to `reflect` or to END when threshold satisfied.

## Observability
Capture per-iteration metrics: tokens, reflection length delta, answer quality score (could be model-graded). Persist alongside versions for regression analysis.

## Summary
This reflection system illustrates a minimal structured self-critique pipeline. By layering iterative loops, research augmentation, and schema-enforced outputs you obtain higher quality, auditable responses with controlled generation behavior.

## Features Demonstrated

### Automated Self-Critique
- AI evaluates its own responses for completeness
- Identifies gaps and weaknesses in generated content
- Structured feedback for improvement guidance

### Research-Driven Improvement
- Automatic generation of relevant search queries
- Targeted information gathering for enhancement
- Evidence-based answer refinement

### Quality Assurance
- Built-in quality control through reflection
- Iterative improvement until quality thresholds met
- Transparent reasoning and improvement process

## Advanced Capabilities

### Structured Reasoning
- Explicit reflection and critique processes
- Documented improvement reasoning
- Traceable decision-making

### Quality Control
- Self-evaluation mechanisms
- Continuous improvement loops
- Quality-driven iteration termination

### Research Integration
- External knowledge integration
- Dynamic information gathering
- Evidence-based enhancement

## Use Cases

### Knowledge Work
- **Research Assistance**: Comprehensive answer generation with self-improvement
- **Content Creation**: High-quality content with built-in review cycles
- **Analysis Tasks**: Self-correcting analytical processes

### Educational Applications
- **Tutoring Systems**: Self-improving explanations
- **Learning Assistance**: Adaptive content enhancement
- **Knowledge Synthesis**: Research-backed information compilation

### Professional Services
- **Consulting**: Self-reviewing recommendations and analysis
- **Technical Writing**: Iteratively improved documentation
- **Decision Support**: Self-correcting decision analysis

## Prerequisites
- Python 3.8+
- LangGraph library
- Pydantic for data validation
- LLM provider with structured output support
- Understanding of agent architectures

## Implementation Patterns

### Reflection Chain Setup
```python
# Reflection workflow implementation
reflection_chain = create_reflection_chain()
improved_answer = reflection_chain.invoke({
    "question": user_question,
    "initial_answer": initial_response
})
```

### Iterative Improvement
```python
current_answer = initial_answer
for iteration in range(max_iterations):
    reflection = generate_reflection(current_answer)
    if meets_quality_threshold(reflection):
        break
    current_answer = improve_answer(current_answer, reflection)
```

### Research Integration
```python
research_queries = generate_research_queries(reflection)
additional_info = gather_information(research_queries)
enhanced_answer = refine_answer(current_answer, additional_info)
```

## Quality Metrics

### Reflection Quality Indicators
- Completeness of missing information identification
- Accuracy of superfluous content detection
- Relevance of suggested improvements

### Answer Quality Measures
- Comprehensiveness of response
- Accuracy of information
- Clarity and structure of explanation

### Improvement Tracking
- Quality progression across iterations
- Research effectiveness measurement
- User satisfaction with final outputs

## Best Practices

### Schema Design
- Clear, descriptive field definitions
- Appropriate optional vs required fields
- Comprehensive validation rules

### Iteration Control
- Maximum iteration limits to prevent infinite loops
- Quality thresholds for termination
- Progress monitoring and logging

### Research Strategy
- Focused, specific research queries
- Reliable information sources
- Evidence validation and integration

## Advanced Features

### Multi-Modal Reflection
- Text, code, and data reflection capabilities
- Domain-specific reflection patterns
- Specialized critique methodologies

### Collaborative Reflection
- Multi-agent reflection systems
- Peer review and critique processes
- Consensus-building mechanisms

### Learning Integration
- Reflection pattern learning and improvement
- Historical reflection analysis
- Adaptive reflection strategies

## Running the System
1. Set up required dependencies and API keys
2. Configure reflection chains and workflows
3. Test with sample questions and scenarios
4. Monitor reflection quality and improvement patterns
5. Iterate on schema and workflow design

## Next Steps
After mastering reflection agents, explore:
- Advanced multi-agent reflection systems
- Domain-specific reflection patterns
- Integration with specialized knowledge bases
- Real-time reflection and improvement systems
- Combination with other agent architectures