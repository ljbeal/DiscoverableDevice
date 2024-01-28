from DiscoverableDevice.Sensor import Sensor
from sensors.bme680 import BME680_I2C


class BME680_MQTT(Sensor):
    """
    Sensor class for a BME680
    """

    def __init__(self, i2c, *args, **kwargs):
        self.sensor = BME680_I2C(i2c=i2c)

        super().__init__("BME680", *args, **kwargs)

    @property
    def signature(self):
        return {
            "temperature": {
                "icon": "mdi:thermometer",
                "unit": "C",
                "value_mod": "round(2)",
            },
            "humidity": {
                "icon": "mdi:water-percent",
                "unit": "%",
                "value_mod": "round(2)",
            },
            "pressure": {"icon": "mdi:weight", "unit": "hPa", "value_mod": "round(2)"},
            "gas_ohms": {"icon": "mdi:omega", "unit": "ohms", "value_mod": "round(2)"},
        }

    def read(self):
        data = self.sensor.data

        for value in data:
            if value in calibration:
                data[value] += calibration[value]

        return data