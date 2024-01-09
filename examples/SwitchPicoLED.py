from DiscoverableDevice.Switch import Switch

from machine import Pin


class SwitchLED(Switch):
    
    def __init__(self, name):        
        
        self._led = Pin("LED", Pin.OUT)
        
        super().__init__(name)
        
    @property
    def led(self):
        return self._led
    
    def setup(self):
        self._state = self.led.value() == 1
        print(f"led setup, initial state {self.state}")

    def callback(self, msg):
        
        print(msg)


if __name__ == "__main__":
    import time
    
    test = SwitchLED(name="test")
    
    for i in range(10):
        time.sleep(1)
        test.toggle()
        
    test.on()
    