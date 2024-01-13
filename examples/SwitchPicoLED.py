from DiscoverableDevice.Switch import Switch

from machine import Pin


class SwitchLED(Switch):
    
    def __init__(self, name):        
        
        self._led = Pin("LED", Pin.OUT)
        
        super().__init__(name)
        
    @property
    def led(self):
        return self._led
    
    @property
    def state(self) -> bool:
        return self.led.value() == 1
    
    def setup(self):
        print(f"led setup, initial state {self.state}")

    def callback(self, msg):
        if msg == "ON":
            self.led.on()
        else:
            self.led.off()


if __name__ == "__main__":
    import time
    
    test = SwitchLED(name="test")
    
    for i in range(10):
        time.sleep(1)
        test.toggle()
        
    test.on()
    