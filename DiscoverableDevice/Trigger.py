"""
Baseclass for a trigger event such as a presence sensor or button.
"""

from DiscoverableDevice.Sensor import Sensor

from machine import Pin
from time import ticks_ms, ticks_diff


class Trigger(Sensor):
    def __init__(self, name, pin):
        super().__init__(name)

        self.integration = "binary_sensor"

        self._irq_callback = None
        self._debounce_time = 0
        self._debounce = 500

        self._queued = False  # set this to true on irq, then false again after a read

        self._gpio_pin = pin
        self._pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self._pin.irq(trigger=Pin.IRQ_FALLING, handler=self.irq_falling)

    @property
    def pin(self):
        return self._pin
    
    @property
    def gpio_pin(self) -> int:
        return self._gpio_pin
    
    def irq_falling(self, pin):
        now = ticks_ms()

        if ticks_diff(now, self._debounce_time) < self._debounce:
            return

        self._debounce_time = now
        self._queued = True
        self._irq_callback(pin)
    
    def set_callback(self, fn):
        self._irq_callback = fn

    @property
    def state_topic(self):
        return f"{self._discovery_prefix}/sensor/{self.parent_uid}/state"

    @property
    def signature(self):
        return {self.name: {"icon": "mdi:toggle-switch", "unit": None}}

    @property
    def value_template(self):
        return f"{{{{ value_json.{self.name}_state }}}}"
    
    def read(self):
        state = "ON" if self._queued else "OFF"
        self._queued = False

        return {f"{self.name}_state": state}


if __name__ == "__main__":
    import time

    test = Trigger("PB", 7)

    while True:
        time.sleep(0.05)

        print(test.read(), end="\r")
