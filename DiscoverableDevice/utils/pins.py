def get_gpio(pin: Pin) -> int:
    return int(str(pin).split("GPIO")[-1].split(",")[0])


if __name__ == "__main__":
    from machine import Pin
    print(get_gpio(Pin(7)))
    print(get_gpio(Pin("LED")))
