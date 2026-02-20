##

from fastapi import FastAPI
from database import SessionLocal
from services.simulate import BaseSensor, SensorManager

app = FastAPI(title="Secure Industrial Data Logger")
# Initialize the sensor manager and add sensors

sensor_manager = SensorManager()
db = SessionLocal()

# Create some example sensors
sensor_manager.add_sensor(BaseSensor("T1", 200, 350, db))
sensor_manager.add_sensor(BaseSensor("P1", 10, 25, db))
sensor_manager.add_sensor(BaseSensor("F1", 5, 15, db))

@app.on_event("startup")
def start_sensors():
    sensor_manager.run()

@app.on_event("shutdown")
def stop_sensors():
    sensor_manager.stop_all()

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API running"}

@app.get("/sensors/latest")
def get_latest_readings():
    readings = db.query(SensorReading).order_by(SensorReading.timestamp.desc()).limit(10).all()
    return readings