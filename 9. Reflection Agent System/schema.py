from pydantic import BaseModel,Field
from typing import List,Optional


class Reflection(BaseModel):
    missing:str=Field(description="Critique of what is missing")
    superfluous: Optional[str] = None

class AnswerQuestion(BaseModel):

    answer:str=Field(description="The answer to the users question in ~250 words")
    search_queries:List[str]=Field(description="1-3 search queries seperately for researching improvements")
    reflection:Reflection=Field(description="Reflection and critique of the initial answer")