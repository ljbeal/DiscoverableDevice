import json

class Sensor:
    def __init__(self, name, icon = None, unit = None):

        if " " in name:
            raise ValueError("names cannot contain spaces")
        
        self._name = name
        self._icon = icon
        self._unit = unit
        
    @property
    def integration(self):
        return "sensor"
    
    @property
    def discovery_prefix(self):
        return self._discovery_prefix
    
    @discovery_prefix.setter
    def discovery_prefix(self, prefix):
        self._discovery_prefix = prefix
        
    @property
    def discovery_topic(self):
        return f"{self._discovery_prefix}/{self.integration}/{self.parent_uid}/{self.name}/config"
    
    def discover(self, mqtt, device_payload, state_topic):
        
        # need a separate discovery for each value a sensor can return                
        payload = self.discovery_payload

        payload["device"] = device_payload
            
        payload["state_topic"] = state_topic 
        
        print(f"discovering on topic {self.discovery_topic}")
        mqtt.publish(self.discovery_topic, json.dumps(payload), retain=True)

    @property
    def parent_uid(self):
        return self._parent_uid
    
    @parent_uid.setter
    def parent_uid(self, uid):
        self._parent_uid = uid
    
    @property
    def name(self):
        return self._name
    
    @property
    def icon(self):
        return self._icon
    
    @property
    def unit(self):
        return self._unit
    
    def value_template(self, name):
        return "{{ " + f"value_json.{name}" + " }}"
    
    @property
    def discovery_payload(self) -> dict:
        """
        Generates a dict to send for discovery
        """
        payload = {}
        # not the right way to do it, but something about pylance hates a direct setup
        payload["unique_id"] = f"{self.parent_uid}_{self.name}"
        payload["icon"] = self.icon
        payload["force_update"] = True
        payload["name"] = self.name
                    
        if self.unit is not None:
            payload["unit_of_measurement"] = self.unit
            payload["value_template"] = "{{ " + f"value_json.{self.name}" + " | round(2) }}"
        else:
            payload["value_template"] = "{{ " + f"value_json.{self.name}" + " }}"
            
        return payload
        
    def read(self):
        raise NotImplementedError
    

def ensure_list(input) -> list:
    """Attempt to coerce `input` to list type"""
    if isinstance(input, list):
        return input
    return [input]


if __name__ == "__main__":
    test = Sensor(name="test")
