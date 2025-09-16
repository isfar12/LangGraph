from langchain.agents import create_react_agent, tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
import datetime
from langchain import hub


search_tool = TavilySearch()

llm=ChatGroq(model="llama-3.3-70b-versatile")

@tool
def current_time() -> str:
    """Get the current time."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

tools=[search_tool, current_time]


from langchain import hub

prompt = hub.pull("hwchase17/react")  # this is the ReAct agent prompt template
agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)


