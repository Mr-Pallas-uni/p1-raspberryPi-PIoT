#A setup
#1. get limits from config.
#2. create db if it doesn't exist.

#B data processing             
#3. get sensehat data.         \
#4. adjust temperature readings.| loop every 10 sec
#5. classify based on config    |
#6. save to db                 /

#C Display
#7. get next sensor from list \ loop every 5 sec
#8. output colour and value   /

#D 

import json


class JsonParser():
    tempMin:float
    tempMax:float
    tempOffset:float
    humidityMin:float
    humidityMax:float
    pressureMin:float
    pressureMax:float
    pitchMax:float
    rollMax:float
    yawMax:float

    def __init__(self) -> None:
        pass


    def validateJson(self) -> None:
        try:
            with open("TaskA/enviro_config.json", "r") as f:
                data = json.load(f)
        except Exception as e:
            print("Error: failed to load config; invalid path, or file at path is not valid Json")
            print(e)
            raise

        current = "Nothing"
        try:
            #Temperature
            current = "temperature - min"
            self.tempMin = data["temperature"]["min"]

            current = "temperature - max"
            self.tempMax = data["temperature"]["max"]

            current = "temperature - offset"
            self.tempOffset = data["temperature"]["offset"]

            #Humidity
            current = "humidity - min"
            self.humidityMin = data["humidity"]["min"]

            current = "humidity - max"
            self.humidityMax = data["humidity"]["max"]
            
            #Pressure
            current = "pressure - min"
            self.pressureMin = data["pressure"]["min"]

            current = "pressure - max"
            self.pressureMax = data["pressure"]["max"]
            
            #Orientation
            current = "orientation - pitch absMax"
            self.pitchMax = data["orientation"]["pitch"]["absMax"]

            current = "orientation - roll absMax"
            self.rollMax = data["orientation"]["roll"]["absMax"]

            current = "orientation - yaw absMax"
            self.yawMax = data["orientation"]["yaw"]["absMax"]

        except Exception:
            print(
                f"Error: failed to load config; JSON structure of '{current}' "
                "was not what was expected."
            )
            raise
    
    def validateRanges(self)-> None:

            # --- Temperature ---
            if self.tempMin >= self.tempMax:
                raise ValueError(f"temperature range invalid: min({self.tempMin}) >= max({self.tempMax})")

            # --- Humidity ---
            if self.humidityMin >= self.humidityMax:
                raise ValueError(f"humidity range invalid: min({self.humidityMin}) >= max({self.humidityMax})")

            # --- Pressure ---
            if self.pressureMin >= self.pressureMax:
                raise ValueError(f"pressure range invalid: min({self.pressureMin}) >= max({self.pressureMax})")

            # --- Orientation ---
            if self.pitchMax <= 0:
                raise ValueError(f"pitch absMax must be > 0, got {self.pitchMax}")

            if self.rollMax <= 0:
                raise ValueError(f"roll absMax must be > 0, got {self.rollMax}")

            if self.yawMax <= 0:
                raise ValueError(f"yaw absMax must be > 0, got {self.yawMax}")





import sqlite3 as lite


con = lite.connect('sensehat.db')
with con: 
    cur = con.cursor() 
    cur.execute("DROP TABLE IF EXISTS SENSEHAT_data")
    cur.execute("CREATE TABLE SENSEHAT_data(timestamp DATETIME, temp NUMERIC)")
#!/usr/bin/env python3
# more info: https://pypi.org/project/python-crontab/

from datetime import datetime
from sense_hat import SenseHat

time = datetime.now().strftime("%H:%M")
sense = SenseHat()
sense.show_message('Time is {}'.format(time), scroll_speed=0.05)

