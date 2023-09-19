import random
from Sensor import Sensor


class BME280:
    """
    Sensor class for a module like a BME280, which returns multiple values per poll
    """
    def __init__(self, name):

        self._sensors = {
            "temp": Sensor("temp", icon="mdi:thermometer", unit="C"),
            "humidity": Sensor("humidity", icon="mdi:water-percent", unit="%"),
            "pressure": Sensor("pressure", icon="mdi:weight", unit="hPa")
        }
    
    @property
    def discovery_prefix(self):
        return self._discovery_prefix
    
    @discovery_prefix.setter
    def discovery_prefix(self, prefix):
        self._discovery_prefix = prefix

        for sensor in self.sensors:
            sensor.discovery_prefix = prefix

    @property
    def parent_uid(self):
        return self._parent_uid
    
    @parent_uid.setter
    def parent_uid(self, uid):
        self._parent_uid = uid

        for sensor in self.sensors:
            sensor.parent_uid = uid

    @property
    def sensors(self):
        return list(self._sensors.values())

    def discover(self, *args, **kwargs):
        print(args)
        print(kwargs)
        for sensor in self.sensors:
            sensor.discover(*args, **kwargs)

    def read(self):
        return {"temp": 20 + random.randint(5, 15), 
                "humidity": 30 + random.randint(1, 30), 
                "pressure": 90 + random.randint(0, 20)
                }


if __name__ == "__main__":
    test = BME280("BME280")
