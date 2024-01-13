from .Sensor import Sensor


class Switch(Sensor):
    
    def __init__(self, name):
        
        if hasattr(self, "setup"):
            # if we have a setup function that ensures an initial state, call it
            self.setup() # type: ignore
        else:
            self._state = False
        
        super().__init__(name)
        
    @property
    def integration(self):
        return "switch"
    
    @property
    def command_topic(self):
        return f"{self.discovery_prefix}/{self.integration}/{self.parent_uid}/{self.name}/set"
    
    def discovery_payload(self, *args, **kwargs):
        """
        Generates a dict to send for discovery
        """
        payload = super().discovery_payload(*args, **kwargs)
        
        return payload
    
    @property
    def state(self):
        return self._state
    
    @property
    def signature(self):
        return {self.name: {"icon": "mdi:toggle-switch", "unit": None}}
    
    def read(self):
        state = "ON" if self.state else "OFF"
        
        name = f"{self.name}_state"
        return {name: state}
    
    def callback(self):
        raise NotImplementedError
