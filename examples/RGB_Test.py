"""
Test for multiple switches, assumes LEDs attached to GPIO pins 21, 18, 16
"""

from DiscoverableDevice.DiscoverableDevice import DiscoverableDevice
from DiscoverableDevice.Switch import Switch

import time
import json
from machine import Pin, PWM


class PWMWrapper:

    def __init__(self, pin: int, freq: int):
        self._pwm = PWM(Pin(pin, Pin.OUT), freq=freq)
        self._value = self._pwm.duty_u16()

    @property
    def value(self):
        return int(255 * self._value / 65535)
    
    @value.setter
    def value(self, val):        
        if val < 0:
            raise RuntimeError("LED values must be between 0 and 255")
        elif val > 255:
            raise RuntimeError("LED values must be between 0 and 255")
        
        if val == 0:
            self._value = 0
        else:
            self._value = int(65535 * val / 255)

        self._update()

    def _update(self):
        self._pwm.duty_u16(self._value)

    def on(self):
        self._pwm.duty_u16(self._value)

    def off(self):
        self._pwm.duty_u16(0)


class RGB(Switch):
    
    _PWMFREQ = 100
    
    def __init__(self, name, pin_r, pin_g, pin_b):        
        
        self._led_r = PWMWrapper(pin_r, freq=RGB._PWMFREQ)
        self._led_g = PWMWrapper(pin_g, freq=RGB._PWMFREQ)
        self._led_b = PWMWrapper(pin_b, freq=RGB._PWMFREQ)
        
        super().__init__(name)

        self.integration = "light"
        self.value_template = None

    @property
    def leds(self):
        return self._led_r, self._led_g, self._led_b

    @property
    def led(self):
        return self._led
    
    @property
    def rgb(self):
        return [self.r, self.g, self.b]
    
    @property
    def r(self):
        return self._led_r.value
    
    @property
    def g(self):
        return self._led_g.value
    
    @property
    def b(self):
        return self._led_b.value
    
    @rgb.setter
    def rgb(self, rgb):
        self._led_r.value = rgb[0]
        self._led_g.value = rgb[1]
        self._led_b.value = rgb[2]

    @r.setter
    def r(self, val):
       self._led_r.value = val
    
    @g.setter
    def g(self, val):
        self._led_g.value = val
    
    @b.setter
    def b(self, val):
        self._led_b.value = val

    def _get_hsv(self) -> [int, float, float]:
        """Generate hsv values from rgb

        from https://www.rapidtables.com/convert/color/hsv-to-rgb.html

        Returns:
            int: Hue from 0 to 360 degrees
            float: Saturation from 0 to 1
            float: Value from 0 to 360
        """
        R_ = self.r/255
        G_ = self.g/255
        B_ = self.b/255

        Cmax = max(R_, G_, B_)
        Cmin = min(R_, G_, B_)
        dC = Cmax - Cmin
        
        if dC == 0:
            H = 0
        elif Cmax == R_:
            H = 60 * ( ( (G_ - B_) / dC) % 6 )
        elif Cmax == G_:
            H = 60 * ( ( (B_ - R_) / dC) + 2 )
        elif Cmax == B_:
            H = 60 * ( ( (R_ - G_) / dC) + 4 )

        if Cmax == 0:
            S = 0
        else:
            S = dC / Cmax

        return H, S, Cmax
    
    @property
    def hsv(self):
        return self._get_hsv()      

    @property
    def hs(self):
        hsv = self.hsv
        return hsv[0], hsv[1]
    
    @hsv.setter
    def hsv(self, hsv):
        H, S, V = hsv

        C = V * S
        X = C * (1 - abs( (H / 60) % 2 - 1) )

        m = V - C

        if H < 60:
            R_, G_, B_ = (C, X, 0)
        elif H < 120:
            R_, G_, B_ = (X, C, 0)
        elif H < 180:
            R_, G_, B_ = (0, C, X)
        elif H < 240:
            R_, G_, B_ = (0, X, C)
        elif H < 300:
            R_, G_, B_ = (X, 0, C)
        else:
            R_, G_, B_ = (C, 0, X)
        
        self.r = (R_ + m) * 255
        self.g = (B_ + m) * 255
        self.b = (G_ + m) * 255

    def callback(self, msg):
        if msg == "ON":
            for led in self.leds:
                led.on()
        elif msg == "OFF":
            for led in self.leds:
                led.off()

        try:
            val = int(msg)
            # TODO: Implement this as a true brightness
            self.rgb = (val, val, val)

        except ValueError:
            pass
    
    @property
    def signature(self):
        return {self.name: {"icon": "mdi:lightbulb"}}
    
    def read(self):        
        state = "ON" if sum(self.rgb) > 0 else "OFF"
        return {f"{self.name}_State": state,
                f"{self.name}_RGB": f"{self.rgb}",
                f"{self.name}_Brightness": 255}
    
    @property
    def extra_discovery_fields(self):
        return {
                "state_value_template": f"{{{{ value_json.{self.name}_State }}}}",
                "rgb_value_template": f"{{{{ value_json.{self.name}_RGB }}}}",
                "rgb_state_topic": f"{self._discovery_prefix}/light/{self.parent_uid}/state",
                "brightness_command_topic": self.command_topic,
                "brightness_value_template": f"{{{{ value_json.{self.name}_Brightness }}}}",
                "payload_on": "ON",
                "payload_off": "OFF",
                }


if __name__ == "__main__":   
    import time

    test = RGB("RGB", 16, 18, 21)

    try:
        for i in range(360):
            test.hsv = (i, 1, 1)
            print(i, test.hsv, test.rgb)
            time.sleep(0.05)
    finally:
        test.rgb = [0, 0, 0]
    