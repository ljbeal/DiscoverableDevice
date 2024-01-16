import random
from DiscoverableDevice.Sensor import Sensor


class BME280(Sensor):
    """
    Sensor class for a module like a BME280, which returns multiple values per poll
    """
    
    @property
    def signature(self):        
        return {"temp": {"icon": "mdi:thermometer",
                         "unit": "C",
                         "value_mod": "round(2)"},
                "humidity": {"icon": "mdi:water-percent",
                             "unit": "%",
                             "value_mod": "round(2)"},
                "pressure": {"icon": "mdi:weight",
                             "unit": "hPa",
                             "value_mod": "round(2)"},
                }

    def read(self):
        return {"temp": 20 + random.randint(5, 15), 
                "humidity": 30 + random.randint(1, 30), 
                "pressure": 90 + random.randint(0, 20)
                }


if __name__ == "__main__":
    test = BME280("BME280")
