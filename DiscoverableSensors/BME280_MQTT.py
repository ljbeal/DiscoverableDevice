from DiscoverableDevice.Sensor import Sensor
from sensors.bme280 import BME280_I2C


class BME280_MQTT(Sensor):
    """
    Sensor class for a BME280
    """

    def __init__(self, i2c, *args, **kwargs):
        self.sensor = BME280_I2C(i2c=i2c)

        super().__init__("BME280", *args, **kwargs)

    @property
    def signature(self):
        return {
            "temperature": {
                "icon": "mdi:thermometer",
                "unit": "C",
                "value_mod": "round(2)"
            },
            "humidity": {
                "icon": "mdi:water-percent",
                "unit": "%",
                "value_mod": "round(2)"
            },
            "pressure": {
                "icon": "mdi:weight", 
                "unit": "hPa", 
                "value_mod": "round(2)"
            },
        }

    def read(self):
        return self.sensor.data
        
    
    
if __name__ == "__main__":
    
    import time
    from machine import Pin, I2C
    
    i2c=I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    
    test = BME280_MQTT(i2c=i2c)

    while True:
        print(test.read())
        time.sleep(1)
