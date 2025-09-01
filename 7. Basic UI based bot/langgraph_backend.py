from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from dotenv import load_dotenv
load_dotenv()


from langchain_groq import ChatGroq

model= ChatGroq(
model="llama-3.3-70b-versatile",
temperature=0.5
)

class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]


def chatnode(state: ChatState):
    messages=state["messages"]
    response = model.invoke(messages)
    return {"messages": [response]}

checkpointer = InMemorySaver()

graph=StateGraph(ChatState)
graph.add_node("chatnode",chatnode)


graph.add_edge(START,"chatnode")
graph.add_edge("chatnode",END)

chatbot=graph.compile(checkpointer=checkpointer)