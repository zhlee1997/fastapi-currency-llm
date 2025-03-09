from typing import List
from datetime import datetime
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class PagingDTO(BaseModel):
    offset: int
    limit: int
    total: int


class TripDTO(BaseModel):
    id: int
    started_at: datetime
    ended_at: datetime
    distance: float
    tip_amount: float
    total_amount: float
    cab_type_id: int

    class Config:
        orm_mode = True


class TripPaginatedResponse(BaseModel):
    results: List[TripDTO]
    paging: PagingDTO


class TelegramMessageRequest(BaseModel):
    """Model for sending telegram message to current user"""

    message: str
