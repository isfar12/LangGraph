from langchain.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.messages import HumanMessage
import datetime
from schema import AnswerQuestion
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticToolsParser
from dotenv import load_dotenv

load_dotenv()


model= ChatGroq(
model="llama-3.3-70b-versatile",
temperature=0.5
)

structured_model=model.with_structured_output(AnswerQuestion)

actor_prompt_template=ChatPromptTemplate.from_messages(
    [
        ("system",'''You are an expert AI researcher
         
        Current date: {current_date}
         
         1. {first_instruction}
         2. Reflect and critique your answer. Be severe to maximize your improvement.
         3. After the reflection, **list  1-3 search queries seperately** for researching improvements.
         Do not inlcude them inside reflection'''),

         MessagesPlaceholder(variable_name="messages"),

         ("system","Answer the users question above using the required format.")
    ]
).partial(current_date=datetime.datetime.now().strftime("%Y-%m-%d"),first_instruction="Answer the users question in ~250 words")


chain = actor_prompt_template | structured_model

result = chain.invoke({
    "messages": [HumanMessage(content="Explain the theory of relativity in simple terms.")]
})
print(result)