
from pydantic import BaseModel, Field
from typing import Literal


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3, max_length=5000)
    category: Literal[
        "account", "billing", "technical", "general","other"
    ] = "general"
    priority: Literal["low", "medium", "high"] = "medium"


class TicketUpdate(BaseModel):
    status: Literal["open", "in_progress", "resolved"]
