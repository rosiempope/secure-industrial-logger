
from database import engine, Base
from models import SensorReading 

Base.metadata.create_all(bind=engine)