from utime import ticks_us, ticks_diff

class Profile:

    __slots__ = ["_name", "_t0"]

    def __init__(self, name: str| None = None):
        self._name = name or "profile"
        self._t0 = ticks_us()

    @property
    def t0(self) -> int:
        return self._t0

    def poll(self) -> float:
        return ticks_diff(ticks_us() , self.t0) / 1000

    def string(self) -> str:
        return f"{self.poll():.2f}ms"


if __name__ == "__main__":
    import time
    
    p = Profile()
    time.sleep(1)

    print(p.string())
