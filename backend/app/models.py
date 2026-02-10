##### This is where every simulated reading will eventually go.
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String, index=True)
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)