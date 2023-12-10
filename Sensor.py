import json

class Sensor:
    def __init__(self, name):

        if " " in name:
            raise ValueError("names cannot contain spaces")
        
        self._name = name
        
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
        for subsensor in self.signature:
            print(f"discovering for subsensor {subsensor}")
            sig = self.signature[subsensor]
            
            icon = sig.get("icon", None)
            unit = sig.get("unit", None)
            
            payload = self.discovery_payload(icon, unit)
            
            payload["device"] = device_payload
                
            payload["state_topic"] = state_topic

            if hasattr(self, "command_topic"):
                payload["command_topic"] = self.command_topic
            
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
    
    def value_template(self, name):
        return "{{ " + f"value_json.{name}" + " }}"
    
    def discovery_payload(self, icon, unit) -> dict:
        """
        Generates a dict to send for discovery
        """
        payload = {}
        # not the right way to do it, but something about pylance hates a direct setup
        payload["unique_id"] = f"{self.parent_uid}_{self.name}"
        payload["icon"] = icon
        payload["force_update"] = True
        payload["name"] = self.name
                    
        if unit is not None:
            payload["unit_of_measurement"] = unit
            payload["value_template"] = "{{ " + f"value_json.{self.name}" + " | round(2) }}"
        else:
            payload["value_template"] = "{{ " + f"value_json.{self.name}" + " }}"
            
        return payload
    
    @property
    def signature(self) -> dict:
        raise NotImplementedError
        
    def read(self) -> dict:
        raise NotImplementedError
    

def ensure_list(input) -> list:
    """Attempt to coerce `input` to list type"""
    if isinstance(input, list):
        return input
    return [input]


if __name__ == "__main__":
    test = Sensor(name="test")
