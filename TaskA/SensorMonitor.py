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
import sqlite3
from sense_hat import SenseHat
import time


class JsonParser():
    def __init__(self) -> None:
        self.validateJson()

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
            float(data["temperature"]["min"])

            current = "temperature - max"
            float(data["temperature"]["max"])

            current = "temperature - offset"
            float(data["temperature"]["offset"])

            #Humidity
            current = "humidity - min"
            float(data["humidity"]["min"])

            current = "humidity - max"
            float(data["humidity"]["max"])
            
            #Pressure
            current = "pressure - min"
            float(data["pressure"]["min"])

            current = "pressure - max"
            float(data["pressure"]["max"])
            
            #Orientation
            current = "orientation - pitch absMax"
            float(data["orientation"]["pitch"]["absMax"])

            current = "orientation - roll absMax"
            float(data["orientation"]["roll"]["absMax"])

            current = "orientation - yaw absMax"
            float(data["orientation"]["yaw"]["absMax"])

        
        except Exception:
            print(
                f"Error: failed to load config; JSON structure of '{current}' "
                "was not what was expected."
            )
            raise
        self.__validateRanges(data)
        self.config = data
        
    
    def __validateRanges(self, config: dict) -> None:
        # Temperature
        if config["temperature"]["min"] >= config["temperature"]["max"]:
            raise ValueError(f"temperature range invalid: min({config['temperature']['min']}) >= max({config['temperature']['max']})")
        
        if config["temperature"]["offset"] <= 0:
            raise ValueError(f"temperature offset must be > 0, got {config['temperature']['offset']}")


        # Humidity
        if config["humidity"]["min"] >= config["humidity"]["max"]:
            raise ValueError(f"humidity range invalid: min({config['humidity']['min']}) >= max({config['humidity']['max']})")

        # Pressure
        if config["pressure"]["min"] >= config["pressure"]["max"]:
            raise ValueError(f"pressure range invalid: min({config['pressure']['min']}) >= max({config['pressure']['max']})")

        # Orientation
        if config["orientation"]["pitch"]["absMax"] <= 0:
            raise ValueError(f"pitch absMax must be > 0, got {config['orientation']['pitchMax']['absMax']}")

        if config["orientation"]["roll"]['absMax'] <= 0:
            raise ValueError(f"roll absMax must be > 0, got {config['orientation']['rollMax']['absMax']}")

        if config["orientation"]["yaw"]['absMax'] <= 0:
            raise ValueError(f"yaw absMax must be > 0, got {config['orientation']['yawMax']['absMax']}")
    
    def asDict(self):
        return self.config
    
class Log():
    config:dict

    def __init__(self, temp, humid, press, pitch, roll, yaw, config) -> None:
        self.config = config
        self.log = {
            "temperature": temp,
            "humidity": humid,
            "pressure": press,
            "pitch": pitch,
            "roll": roll,
            "yaw": yaw,
            "temperature class": "",
            "humidity class": "",
            "pressure class": "",
            "pitch class": "",
            "roll class": "",
            "yaw class": ""
        }

        self.setTemp(temp)
        self.setHumid(humid)
        self.setPress(press)
        self.setPitch(pitch)
        self.setRoll(roll)
        self.setYaw(yaw)

    def setTemp(self, temp):
        self.log["temperature"] = temp - self.config["temperature"]["offset"]

        if temp < self.config["temperature"]["min"]:
            self.log["temperature class"] = "low"
        elif temp > self.config["temperature"]["max"]:
            self.log["temperature class"] = "high"
        else:
            self.log["temperature class"] = "comfortable"

    def setHumid(self, humid):
        self.log["humidity"] = humid

        if humid < self.config["humidity"]["min"]:
            self.log["humidity class"] = "low"
        elif humid > self.config["humidity"]["max"]:
            self.log["humidity class"] = "high"
        else:
            self.log["humidity class"] = "comfortable"

    def setPress(self, press):
        self.log["pressure"] = press

        if press < self.config["pressure"]["min"]:
            self.log["pressure class"] = "low"
        elif press > self.config["pressure"]["max"]:
            self.log["pressure class"] = "high"
        else:
            self.log["pressure class"] = "normal"

    def setPitch(self, pitch):
        self.log["pitch"] = pitch

        if abs(pitch) > self.config["orientation"]["pitch"]['absMax']:
            self.log["pitch class"] = "tilted"
        else:
            self.log["pitch class"] = "aligned"

    def setRoll(self, roll):
        self.log["roll"] = roll

        if abs(roll) > self.config["orientation"]["roll"]['absMax']:
            self.log["roll class"] = "tilted"
        else:
            self.log["roll class"] = "aligned"

    def setYaw(self, yaw):
        self.log["yaw"] = yaw

        if abs(yaw) > self.config["orientation"]["yaw"]['absMax']:
            self.log["yaw class"] = "tilted"
        else:
            self.log["yaw class"] = "aligned"

    def asDict(self):
        return self.log 

class SqlManager():
    def __init__(self) -> None:
        self.initDB()
        pass

    def initDB(self) -> None:
        con = sqlite3.connect('sensehat.db')
        with con: 
            cur = con.cursor() 
            cur.execute("DROP TABLE IF EXISTS SENSEHAT_data")
            cur.execute("CREATE TABLE SENSEHAT_data(timestamp DATETIME, temp NUMERIC, tempClass NUMERIC, humid NUMERIC," \
            " humidClass NUMERIC, press NUMERIC, pressClass NUMERIC, " \
            "pitch NUMERIC, pitchClass NUMERIC, roll NUMERIC," \
            " rollClass NUMERIC, yaw NUMERIC, yawClass NUMERIC)")

    def LogData(self,log:dict):
        conn=sqlite3.connect("sensehat.db")
        curs=conn.cursor()
        curs.execute("INSERT INTO SENSEHAT_data values(datetime('now'), \
                     ?, ?, ?, \
                      ?, ?, ?, \
                      ?, ?, ?, \
                      ?, ?, ?)", (  log["temperature"], log["temperature class"], log["humidity"],
                                     log["humidity class"], log["pressure"], log["pressure class"],
                                     log["pitch"], log["pitch class"], log["roll"], 
                                     log["roll class"], log["yaw"], log["yaw class"],))
        conn.commit()
        conn.close()

class Sensor():
    def __init__(self, config) -> None:
        self.config = config
        self.sense = SenseHat()

    def getSenseLog(self)-> dict:
        temp = self.sense.get_temperature()
        humid = self.sense.get_humidity()
        press = self.sense.get_pressure()
        pitch = self.sense.get_orientation()["pitch"]
        roll = self.sense.get_orientation()["roll"]
        yaw = self.sense.get_orientation()["yaw"]
        log = Log(temp,humid,press,pitch,roll,yaw, self.config).asDict()
        return log

class Display():
    def __init__(self) -> None:
        self.sense = SenseHat()
        self.cheatSheet = {
            "T":["temperature" ,"temperature class"],
            "H":["humidity", "humidity class"],
            "P":["pressure", "pressure class"],
            "Pi":["pitch", "pitch class"],
            "Ro":["roll", "roll"],
            "Ya":["yaw", "yaw"]
            }
        
        self.order = ["T", "H", "P", "Pi", "Ro", "Ya"]
        self.currIndex = 0
    
    def updateLog(self,log:dict):
        self.log = log
        
    def displayNext(self):
        print("displaying!!!!")
        #get the next sense in the list, loop back around to the start if we've reached the end
        self.currIndex = (self.currIndex + 1)%len(self.order)
        currSenseShort = self.order[self.currIndex]

        #get what the sense is called in the log.
        currSense = self.cheatSheet[currSenseShort][0]
        currVal = self.log[currSense]

        #get the classification of the sense.
        currSenseClass = self.cheatSheet[currSenseShort][1]
        currClass = self.log[currSenseClass]

        message = f"{currSenseShort}: {currVal}"

        colour = self.getDisplayColour(currClass)
        self.sense.show_message(message, scroll_speed=0.05, back_colour= colour)

    def getDisplayColour(self,classification:str):
        if classification == "low":
            colour = [40,66,100]
        elif classification == "high":
            colour = [75,5,5]
        elif classification == "comfortable":
            colour = [5,90,5]
        elif classification == "normal":
            colour = [5,90,5]
        elif classification == "tilted":
            colour = [100,80,0]
        elif classification == "aligned":
            colour = [5,90,5]
        else:
            #error colour in case something goes wrong.
            colour = [100,0,80]
        return colour

def main():
    
    displayWait = 5
    logWait = 10     

    #instantiate all the parts
    config = JsonParser().asDict()
    sql = SqlManager()
    s = Sensor(config)
    d = Display()

    logTime = time.time()
    displayTime = time.time()

    #trigger everything once before the code starts looping.
    log = s.getSenseLog()
    sql.LogData(log)
    d.updateLog(log)
    d.displayNext()

    for _ in range (0,11):
        currTime = time.time()

        if  currTime - logTime > logWait:
            log = s.getSenseLog()
            sql.LogData(log)
            d.updateLog(log)

            #reset time
            logTime = time.time()

        if currTime - displayTime > displayWait:
            d.displayNext()

            #reset time
            displayTime = time.time()
        time.sleep(1)


# Execute program 
main()



