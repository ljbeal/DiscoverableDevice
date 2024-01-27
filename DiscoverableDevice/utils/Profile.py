from time import ticks_us, ticks_diff


class Profile:

    def __init__(self):
        self._t0 = ticks_us()

    @property
    def t0(self):
        return self._t0
    
    @property
    def dt(self):
        return ticks_diff(ticks_us(), self.t0)
    
    def string(self):
        return f"{self.dt/1000:.2f}ms"
    

if __name__ == "__main__":
    from time import sleep

    p = Profile()
    sleep(1)
    print(p.string())
