from Sensor import Sensor

import machine

class CPUTemp(Sensor):
        
    def read(self):    
        adc = machine.ADC(4)
        
        voltage = adc.read_u16() * (3.3 / 65536)
        
        temp_c = 27 - ( voltage - 0.706) / 0.001721
        
        return temp_c
    

if __name__ == "__main__":
    test = CPUTemp(name="test",
                   icon="",
                   unit="C",
                   parent_uid="")
    
    print(test.read())    
