from DiscoverableDevice.Switch import Switch

from machine import Pin


class SwitchLED(Switch):

    def __init__(self, name):

        self._led = Pin("LED", Pin.OUT)

        super().__init__(name)

        self.integration = "light"
        self.value_template = None

    @property
    def led(self):
        return self._led
    
    @property
    def state(self) -> bool:
        return self.led.value() == 1

    def callback(self, msg):
        if msg == "ON":
            self.led.on()
        else:
            self.led.off()
    
    @property
    def signature(self):
        return {self.name: {"icon": "mdi:toggle-switch"}}
    
    def read(self):
        state = "ON" if self.state else "OFF"
        
        return {self.name: state}
    
    @property
    def extra_discovery_fields(self):
        return {"payload_on": "ON",
                "payload_off": "OFF",
                "state_value_template": "{{ value_json.BoardLED }}"}


if __name__ == "__main__":
    import time
    
    test = SwitchLED(name="test")
    
    for i in range(10):
        time.sleep(1)
        test.toggle()
        
    test.on()
    