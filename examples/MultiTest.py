import random
from Sensor import Sensor


class BME280:
    """
    Sensor class for a module like a BME280, which returns multiple values per poll
    """
    
    @property
    def signature(self):
        
        return {"temp": {"icon": "mdi:thermometer",
                         "unit": "C"},
                "humidity": {"icon": "mdi:water-percent",
                             "unit": "%"},
                "pressure": {"icon": "mdi:weight",
                             "unit": "hPa"},
                }

    def read(self):
        return {"temp": 20 + random.randint(5, 15), 
                "humidity": 30 + random.randint(1, 30), 
                "pressure": 90 + random.randint(0, 20)
                }


if __name__ == "__main__":
    test = BME280("BME280")
