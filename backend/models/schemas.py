from pydantic import BaseModel,Field
from typing import Literal


class ChatRequest(BaseModel):
    message : str = Field(min_length= 1 , max_length = 12000)

    risk : Literal['low', 'medium', 'high'] = 'low' 
    # this line means if the user forget to assign the risk level so it automatically be assigned as low risk


class ChatResponse(BaseModel):
    answer : str
    model_route :  str
    input_token :  int
    output_token : int
    estimated_cost_usd : float
    needs_human_review : bool = False
