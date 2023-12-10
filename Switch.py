from Sensor import Sensor


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
        return f"{self.discovery_prefix}/switch/{self.parent_uid}/{self.name}/set"
    
    @property
    def discovery_payload(self, icon, unit):
        """
        Generates a dict to send for discovery
        """
        payload = {}
        # not the right way to do it, but something about pylance hates a direct setup
        payload["unique_id"] = f"{self.parent_uid}_{self.name}"
        payload["icon"] = icon
        payload["force_update"] = True
        payload["name"] = self.name
        
        payload["value_template"] = "{{ " + f"value_json.{self.name}_state" + " }}"
        
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
    