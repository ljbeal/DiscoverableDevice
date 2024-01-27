from time import time_us, ticks_diff


class Profile:

    def __init__(self):
        self._t0 = time_us()

    @property
    def t0(self):
        return self._t0
    
    @property
    def dt(self):
        return ticks_diff(time_us(), self.t0)
    
    def string(self):
        return f"{self.dt/1000/.2f}ms"
