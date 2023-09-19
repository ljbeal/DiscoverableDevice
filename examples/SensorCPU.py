from Sensor import Sensor

import machine

class CPUTemp(Sensor):
    def __init__(self, name: str | list):
        icon = "mdi:thermometer"
        unit = "C"
        super().__init__(name, icon, unit)
        
    def read(self):    
        adc = machine.ADC(4)
        
        voltage = adc.read_u16() * (3.3 / 65536)
        
        temp_c = 27 - ( voltage - 0.706) / 0.001721
        
        return temp_c
    

if __name__ == "__main__":
    test = CPUTemp(name="test")
    
    print(test.read())    
