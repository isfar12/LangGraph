from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.output_parsers import PydanticToolsParser
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()


class Reflection(BaseModel):
    missing: str = Field(..., description="Critique what informations are missing")
    superfluous: str = Field(..., description="Critique what informations are superfluous")

class Answer(BaseModel):
    answer: str = Field(..., description="The answer to the user's question")
    reflection: Reflection = Field(..., description="Reflection on the provided answer")


answer_parser = PydanticToolsParser(tools=[Answer])




model=ChatGroq(model="openai/gpt-oss-20b", temperature=0)

template = """You are a highly intelligent question answering bot.
You will be provided with a question, and a set of context information.
You will first answer the question based on the context information.
Then, you will reflect on your answer and critique what informations are missing
and what informations are superfluous.  
Finally, you will provide your final answer and your reflection in a json format.
Use the following format:
{{
"answer": "your answer",
"reflection": {{
"missing": "what is missing",
"superfluous": "what is superfluous"
}}
}}
Use the following context information to answer the question:
{context}
Question: {question}
Answer:"""

prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=template
)

chain = prompt | model.bind_tools(tools=[Answer],tool_choice="Answer") | answer_parser

response = chain.invoke({
    "context": "The capital of France is Paris. The capital of Germany is Berlin.",
    "question": "What are the capitals of France and Germany?"
})

print(response)