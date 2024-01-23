from .Sensor import Sensor


class Switch(Sensor):
    
    def __init__(self, name):
        
        if hasattr(self, "setup"):
            # if we have a setup function that ensures an initial state, call it
            self.setup() # type: ignore
        else:
            self._state = False
        
        super().__init__(name)
        
        self.integration = "switch"
    
    @property
    def command_topic(self):
        return f"{self.base_topic}/{self.name}/set"
    
    def discovery_payload(self, *args, **kwargs):
        """
        Generates a dict to send for discovery
        """
        payload = super().discovery_payload(*args, **kwargs)
        
        return payload
    
    @property
    def signature(self):
        raise NotImplementedError
    
    def read(self):
        raise NotImplementedError
    
    def callback(self, msg):
        """Implement function call to handle incoming `msg`"""
        raise NotImplementedError
