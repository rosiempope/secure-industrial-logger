#this is making fake data for testing purposes, it is not used in production. 
#It is trying to make temperature, pressure & flow data for a given number of hours, with a given frequency.

import random
from datetime import datetime
from models import SensorReading
from database import get_db

class BaseSensor:
    def __init__(self, sensor_id, min_value, max_value, db_session):
        self.sensor_id = sensor_id
        self.min_value = min_value
        self.max_value = max_value
        self.db_session = db_session #??

    def generate_reading(self):
        value = round(random.uniform(self.min_value, self.max_value), 2) 
        #making some readings from the sensor - between our defined limits to 
        #try simualte real collecting data from a sensor
        return {
            "sensor_id": self.sensor_id,
            "value": value,
            "timestamp": datetime.utcnow()
        }

    def save_reading(self, reading):
        db_session = next(get_db())
        db_reading = SensorReading(**reading)
        db_session.add(db_reading)
        db_session.commit()
        db_session.close()


import threading
import time

class SensorManager:
    def __init__(self):
        self.sensors = []
        self.threads = []
        self.running = False

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def _sensor_loop(self, sensor, interval=2):
        while self.running:
            reading = sensor.generate_reading()
            sensor.save_reading(reading)
            print(f"Saved {reading}")
            time.sleep(interval)

    def run(self):
        self.running = True
        for sensor in self.sensors:
            t = threading.Thread(target=self._sensor_loop, args=(sensor,))
            t.start()
            self.threads.append(t)

    def stop_all(self):
        self.running = False
        for t in self.threads:
            t.join()
