from sqlalchemy import Column, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TripRecord(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=False)
    distance = Column(Float, nullable=False)
    tip_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    cab_type_id = Column(Integer, nullable=False)
