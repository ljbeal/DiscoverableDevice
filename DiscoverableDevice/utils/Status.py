from time import ticks_ms, ticks_diff
from machine import Pin


def blink(length, interval: float = 0.5):
    led = Pin("LED", Pin.OUT)

    t0 = ticks_ms()
    last_blink = ticks_ms()

    while ticks_diff(ticks_ms(), t0) < length * 1000:
        if ticks_diff(ticks_ms(), last_blink) > interval * 1000:
            last_blink = ticks_ms()
            led.toggle()

    led.off()


if __name__ == "__main__":
    blink(10)
