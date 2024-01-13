from DiscoverableDevice.Switch import Switch

from machine import Pin, PWM


class Dimmer(Switch):
    
    def __init__(self, name):        
        
        self._pwm = PWM(Pin(21, Pin.OUT), freq=100000)
        
        super().__init__(name)
        
    @property
    def pwm(self):
        return self._pwm
    
    @property
    def integration(self):
        return "light"
    
    @property
    def duty(self):
        """Get PWM duty cycle

        Returns:
            float: duty between 0 and 1
        """
        return self.pwm.duty_u16() / 65535
    
    @duty.setter
    def duty(self, val: float):
        """Set duty cycle

        Args:
            val (float): target duty between 0 and 1
        """
        if val > 1:
            raise ValueError("Duty cycle {val} > 0.1!")
        
        target = round(val * 65535)
        print(f"setting duty_u16 to {target}")
        self.pwm.duty_u16(target)
    
    def setup(self):
        print(f"led setup, initial duty {self.duty}")

    def callback(self, msg):
        try:
            val = int(msg)

            self.duty = val / 255
            
        except AttributeError:
            print(f"could not parse message {msg}")
    
    def read(self):
        state = "ON" if self.duty > 0.0 else "OFF"
        
        return {f"{self.name}_state": state, 
                f"{self.name}_brightness": round(self.duty * 255)}
    
    @property
    def value_template(self):
        return "{{ " +  f"value_json.{self.name}_state" + " }}"
    
    @property
    def extra_discovery_fields(self):
        return {"brightness_value_template": "{{ " +  f"value_json.{self.name}_brightness | int" + " }}",
                "brightness_state_topic": self.state_topic,
                "brightness_command_topic": self.command_topic,
                "brightness": True,
                "effect": True,
                "effect_list": ["solid"],
                "on_command_type": "brightness",
                }


if __name__ == "__main__":
    import time

    test = Dimmer(name="DimmerTest")

    for i in range(11):
        time.sleep(0.1)

        test.duty = i/10

    for i in range(11):
        time.sleep(0.1)

        test.duty = 1 - i/10
    