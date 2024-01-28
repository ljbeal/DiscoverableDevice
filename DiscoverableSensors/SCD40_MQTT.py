from DiscoverableDevice.Sensor import Sensor
from sensors.scd4x import SCD4X


class SCD40_MQTT(Sensor):
        def __init__(self, i2c):
            self.sensor = SCD4X(i2c)

            self.sensor.start_periodic_measurement()

            super().__init__("SCD40")

        @property
        def signature(self):
            return {
                "temperature_scd40": {
                    "icon": "mdi:thermometer",
                    "unit": "C",
                    "value_mod": "round(2)",
                },
                "humidity_scd40": {
                    "icon": "mdi:water-percent",
                    "unit": "%",
                    "value_mod": "round(2)",
                },
                "CO2": {
                    "icon": "mdi:molecule-co2",
                    "unit": "ppm",
                    "value_mod": "round(2)",
                },
            }

        def read(self):
            data = self.sensor.read()

            data["temperature_scd40"] = data.pop("temperature")
            data["humidity_scd40"] = data.pop("humidity")

            for value in data:
                if value in calibration:
                    try:
                        data[value] += calibration[value]
                    except TypeError:
                        continue

            return data