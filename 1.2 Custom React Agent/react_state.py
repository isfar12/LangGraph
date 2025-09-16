import operator
from typing import Any, Dict, List, Optional,Annotated,Union,TypedDict

from langchain_core.agents import AgentAction, AgentFinish

class ReactAgentState(TypedDict):
    """State for the React Agent."""
    input:str
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps:Annotated[list[tuple[AgentAction, str]],operator.add]
    
