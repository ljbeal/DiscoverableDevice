from DiscoverableDevice.Trigger import Trigger


class SR501_MQTT(Trigger):
    def __init__(self, name, pin, debounce=5000, warmup=45):
        super().__init__(name, pin, debounce)

        self._init_time = time.time()
        self._warmup = warmup
        print(f"init SR501 at {self._init_time}")

    @property
    def warmup(self):
        if time.time() <= self._init_time + self._warmup:
            return True
        return False

    @property
    def triggered(self):
        return self.pin.value() == 1

    def read(self):
        name = f"{self.name}_state"
        # If we are still in the warmup period, do nothing
        if self.warmup:
            print("SR501 is warming up")
            return

        val = "OFF"
        if self.triggered:
            # primitive "debounce"
            time.sleep(2)

            if self.triggered:
                val = "ON"

        return {name: val}
