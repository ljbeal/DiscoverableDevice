from Switch import Switch

from machine import Pin


class SwitchLED(Switch):
    
    def __init__(self, name, **kwargs):        
        
        self._led = Pin("LED", Pin.OUT)
        
        super().__init__(name, **kwargs)
        
    @property
    def led(self):
        return self._led
    
    def setup(self):
        self._state = self.led.value() == 1
        print(f"led setup, initial state {self.state}")
    
    def toggle(self):
        self.led.toggle()
        self._state = self.state == False
        
    def on(self):
        self.led.value(1)
        self._state = True
        
    def off(self):
        self.led.value(0)
        self._state = False


if __name__ == "__main__":
    import time
    
    test = SwitchLED(name="test",
                     parent_uid="")
    
    for i in range(10):
        time.sleep(1)
        test.toggle()
        
    test.on()
    