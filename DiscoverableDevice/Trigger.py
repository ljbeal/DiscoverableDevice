"""
Baseclass for a trigger event such as a presence sensor or button.
"""

from DiscoverableDevice.Sensor import Sensor
from machine import Pin


class Trigger(Sensor):
    def __init__(self, name, pin):
        super().__init__(name)

        self._pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)

    @property
    def pin(self):
        return self._pin

    @property
    def integration(self):
        return "binary_sensor"

    @property
    def state_topic(self):
        return f"{self._discovery_prefix}/sensor/{self.parent_uid}/state"

    @property
    def triggered(self):
        return self.pin.value() == 1

    @property
    def signature(self):
        return {self.name: {"icon": "mdi:account", "unit": None}}

    def read(self):
        val = "ON" if self.triggered else "OFF"

        name = f"{self.name}_state"
        return {name: val}

    @property
    def value_template(self):
        return f"{{{{ value_json.{self.name}_state }}}}"


if __name__ == "__main__":
    import time

    test = Trigger("presence", 15)

    while True:
        time.sleep(0.05)

        print(test.read(), end="\r")
