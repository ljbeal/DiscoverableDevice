from Sensor import Sensor


class Switch(Sensor):
    
    def __init__(self, name):
        
        unit = None  # units don't make sense for a switch
        icon = "mdi:toggle-switch"  # enforce toggle for now
        
        if hasattr(self, "setup"):
            # if we have a setup function that ensures an initial state, call it
            self.setup() # type: ignore
        else:
            self._state = False
        
        super().__init__(name, icon, unit)
        
    @property
    def integration(self):
        return "switch"
    
    @property
    def discovery_payload(self):
        payload = {"unique_id": f"{self.parent_uid}_{self.name}",
                   "icon": self.icon,
                   "command_topic": self.command_topic,
                   "force_update": True,
                   "name": self.name
                   }
        
        payload["value_template"] = "{{ " + f"value_json.{self.name}" + " }}"
                   
        return payload
    
    @property
    def command_topic(self):
        return f"{self.discovery_prefix}/switch/{self.parent_uid}/{self.name}/set"
    
    @property
    def state(self):
        return self._state
    
    def read(self):
        return "ON" if self.state else "OFF"
    
    def toggle(self):
        raise NotImplementedError
    