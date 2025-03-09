from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends
from starlette import status
from sqlalchemy.orm import Session

from app.services.trip_service import TripService
from app.persistence.session import get_db
from app.api.models import TripPaginatedResponse

router = APIRouter()


@router.get("/trips")
def trips():
    return {"hello": "world"}


@router.get(
    "/get_trips",
    status_code=status.HTTP_200_OK,
    response_model=TripPaginatedResponse,
    tags=["Call Data"],
)
def get_trips(
    start_date: datetime = Query(
        ...,
        title="Start Date",
        description="The start date of the filter",
        alias="start_date",
    ),
    end_date: datetime = Query(
        ...,
        title="End Date",
        description="The end date of the filter",
        alias="end_date",
    ),
    offset: int = Query(0, title="Offset", description="The offset for paging"),
    limit: int = Query(100, title="Limit", description="The limit for paging"),
    db: Session = Depends(get_db),
):
    results = TripService.get_trips(db, start_date, end_date, offset, limit)

    if results is None:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Records not found"
        )
    return results
