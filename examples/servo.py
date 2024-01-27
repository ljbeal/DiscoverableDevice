from DiscoverableDevice.Switch import Switch

from machine import Pin, PWM
        


class HAServo(Switch):
    
    def __init__(self, name, pin):
        self._state = False

        print(f"pwm on pin {pin}")
        self._pwm = PWM(Pin(pin, Pin.OUT))

        self._pwm.duty_u16(1638)
        
        super().__init__(name)  

    @property
    def signature(self):
        return {}
    
    @property
    def integration(self):
        return "switch"
    
    @property
    def servo(self):
        return self._servo

    @property
    def state_topic(self):
        return f"{self._discovery_prefix}/sensor/{self.parent_uid}/state"
    
    def setup(self):
        print(f"led setup, initial state {self.state}")

    def callback(self, msg):
        if msg == "ON":
            dmin = 1638
            print(f"duty to {dmin}")
            self._pwm.duty_u16(dmin)
        else:
            dmax = 7864
            print(f"duty to {dmax}")
            self._pwm.duty_u16(dmax)

    @property
    def state(self):
        return self._state
    
    @property
    def signature(self):
        return {self.name: {"icon": "mdi:toggle-switch"}}
    
    def read(self):
        state = "ON" if self.state else "OFF"
        
        return {self.name: state}
    
    @property
    def extra_discovery_fields(self):
        return {"payload_on": "ON",
                "payload_off": "OFF"}


if __name__ == "__main__":
    import time
    
    test = SwitchLED(name="test")
    
    for i in range(10):
        time.sleep(1)
        test.toggle()
        
    test.on()
    