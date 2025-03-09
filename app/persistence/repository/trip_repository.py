from datetime import datetime
from sqlalchemy.orm import Session

from app.api.models import TripPaginatedResponse, TripDTO, PagingDTO
from app.persistence.schemas import TripRecord


class TripRepository:

    @staticmethod
    def get_trips(
        db: Session, start_date: datetime, end_date: datetime, offset: int, limit: int
    ):
        trips = (
            db.query(TripRecord)
            .filter(
                TripRecord.started_at >= start_date, TripRecord.started_at <= end_date
            )
            .offset(offset)
            .limit(limit)
            .all()
        )
        total = (
            db.query(TripRecord)
            .filter(
                TripRecord.started_at >= start_date, TripRecord.started_at <= end_date
            )
            .count()
        )
        return TripPaginatedResponse(
            results=[TripDTO.from_orm(trip) for trip in trips],
            paging=PagingDTO(limit=limit, offset=offset, total=total),
        )
