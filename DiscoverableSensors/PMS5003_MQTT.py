from DiscoverableDevice.Sensor import Sensor
from sensors.pms5003 import PMS5003


class PMS5003_MQTT(Sensor):
    def __init__(self, uart, pin_enable, pin_reset):
        self.sensor = pms5003 = PMS5003(
            uart=uart,
            pin_enable=machine.Pin(pin_enable),
            pin_reset=machine.Pin(pin_reset),
            mode="active",
        )

        super().__init__("PMS5003")

    @property
    def signature(self):
        return {
            "PM1_0": {
                "icon": "mdi:spray",
                "unit": "ug/m3",
                "value_mod": "round(2)",
            },
            "PM2_5": {
                "icon": "mdi:bacteria-outline",
                "unit": "ug/m3",
                "value_mod": "round(2)",
            },
            "PM10": {
                "icon": "mdi:liquid-spot",
                "unit": "ug/m3",
                "value_mod": "round(2)",
            },
        }

    def read(self):
        raw = self.sensor.read().data

        data = {"PM1_0": raw[0], "PM2_5": raw[1], "PM10": raw[2]}

        return data