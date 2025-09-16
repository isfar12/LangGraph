from agent_reason_runnable import agent,tools
from react_state import ReactAgentState


def reason_node(state:ReactAgentState):
    agent_outcome=agent.invoke(state)
    return {"agent_outcome":agent_outcome}




def act_node(state:ReactAgentState):
    agent_action=state["agent_outcome"]
    
    tool_name=agent_action.tool
    tool_input=agent_action.tool_input

    tool_function=None
    for tool in tools:
        if tool.name==tool_name:
            tool_function=tool
            break

    if tool_function:
        if isinstance(tool_input,dict):
            observation=tool_function.invoke(**tool_input)
        else:
            observation=tool_function.invoke(tool_input)
    else:
        observation=f"Tool {tool_name} not found."

    return {
        "intermediate_steps":[(agent_action,str(observation))]
    }