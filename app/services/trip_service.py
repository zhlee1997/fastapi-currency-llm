from datetime import datetime
from sqlalchemy.orm import Session

from app.persistence.repository.trip_repository import TripRepository


class TripService:
    @staticmethod
    def get_trips(
        db: Session, start_date: datetime, end_date: datetime, offset: int, limit: int
    ):
        return TripRepository.get_trips(db, start_date, end_date, offset, limit)
