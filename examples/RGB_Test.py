"""
Test for multiple switches, assumes LEDs attached to GPIO pins 21, 18, 16
"""

from DiscoverableDevice import DiscoverableDevice

import time

import machine

from Switch import Switch


class LED(Switch):
    def __init__(self, pin: int, *args, **kwargs):
        # print(f"setting up LED on pin {pin}")
        self._pin = machine.Pin(pin, machine.Pin.OUT)

        super().__init__(*args, **kwargs)
        
    @property
    def led(self):
        return self._pin
    
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
    import secrets as s
    
    import rp2
    import network
    
    rp2.country('FR')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
        
    msg = "Connecting\nto WiFi"
    wlan.connect(s.wifi["ssid"], s.wifi["pass"])

    while not wlan.isconnected() and wlan.status() >= 0:
        time.sleep(1)
        
    print("wifi connected")
    
    test = DiscoverableDevice(wlan,
                              host=s.mqtt["host"],
                              user=s.mqtt["user"],
                              password=s.mqtt["pass"],
                              location="Desk",
                              interval=5)
    
    # adding sensors and switches
    from examples.SensorCPU import CPUTemp
    from examples.SwitchPicoLED import SwitchLED
    
    test.add_sensor("cpu_temp", "mdi:thermometer", "C", CPUTemp)
    test.add_switch("BoardLED", SwitchLED)

    test.add_switch("LED_R", LED, 21)
    test.add_switch("LED_G", LED, 18)
    test.add_switch("LED_B", LED, 16)
    
    # run indefinitely
    test.run()
    