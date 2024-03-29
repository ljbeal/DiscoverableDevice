from DiscoverableDevice.Sensor import Sensor

import machine

class CPUTemp(Sensor):
    
    @property
    def signature(self):
        return {"cputemp": {"icon": "mdi:thermometer",
                            "unit": "C",
                            "value_mod": "round(2)"}
                }
        
    def read(self):    
        adc = machine.ADC(4)
        
        voltage = adc.read_u16() * (3.3 / 65536)
        
        temp_c = 27 - ( voltage - 0.706) / 0.001721
        
        return {"cputemp": temp_c}
    

if __name__ == "__main__":
    test = CPUTemp(name="test")
    
    print(test.read())    
