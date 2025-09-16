from dotenv import load_dotenv
load_dotenv()

from langchain_core.agents import AgentFinish, AgentAction
from langgraph.graph import START,END,StateGraph
from nodes import reason_node,act_node
from react_state import ReactAgentState


REASON_NODE = "reason_node"
ACT_NODE = "act_node"

def should_continue(state:ReactAgentState):
    if isinstance(state["agent_outcome"], AgentFinish):
        return END
    else:
        return ACT_NODE
    
graph=StateGraph(ReactAgentState)
graph.add_node(REASON_NODE,reason_node)
graph.add_node(ACT_NODE,act_node)

graph.add_edge(START,REASON_NODE)
graph.add_conditional_edges(REASON_NODE,should_continue)
graph.add_edge(ACT_NODE,REASON_NODE)

workflow=graph.compile()

result=workflow.invoke({"input":"What is the current time in New York and who is the president of the United States?"})
print(result)
