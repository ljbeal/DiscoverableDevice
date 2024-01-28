from DiscoverableDevice.Sensor import Sensor
from sensors.bh1750 import BH1750 as BH1750


class BH1750_MQTT(Sensor):
    """
    Sensor class for a BH1750
    """

    def __init__(self, i2c, *args, **kwargs):
        self.sensor = BH1750(i2c)

        super().__init__("BH1750", *args, **kwargs)

    @property
    def signature(self):
        return {"lightlevel": {"icon": "mdi:weather-sunny", "unit": "lx"}}

    def read(self):
        val = self.sensor.luminance(BH1750_I2C.ONCE_HIRES_1)

        if "lightlevel" in calibration:
            val += calibration["lightlevel"]

        return {"lightlevel": val}