from Sensor import Sensor


class Switch(Sensor):
    
    def __init__(self, names):
        
        units = [None]  # units don't make sense for a switch
        icons = ["mdi:toggle-switch"]  # enforce toggle for now
        
        if hasattr(self, "setup"):
            # if we have a setup function that ensures an initial state, call it
            self.setup() # type: ignore
        else:
            self._state = False
        
        super().__init__(names, icons, units)
        
    @property
    def integration(self):
        return "switch"
    
    @property
    def command_topics(self):
        output = []
        for name in self.names:
            output.append(f"{self.discovery_prefix}/switch/{self.parent_uid}/{name}/set")

        return output
    
    def discover(self):
        output = {}
        for name, icon, ctopic in zip(self.names, self.icons, self.command_topics):
            payload = {}
                
            payload["unique_id"] = f"{self.parent_uid}_{name}"
            payload["icon"] = icon
            payload["command_topic"] = ctopic
            payload["name"] = name
            
            payload["value_template"] = "{{ " + f"value_json.{name}" + " }}"

            topic = f"{self._discovery_prefix}/{self.integration}/{self.parent_uid}/{name}/config"

            output[topic] = payload
            
        return output
    
    @property
    def state(self):
        return self._state
    
    def read(self):
        return "ON" if self.state else "OFF"
    
    def toggle(self):
        raise NotImplementedError
    