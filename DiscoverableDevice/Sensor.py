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
        
    def discovery_topic(self, subsensor=None):
        if subsensor is None:
            name = self.name
        else:
            name = f"{self.name}_{subsensor}"
            
        return f"{self._discovery_prefix}/{self.integration}/{self.parent_uid}/{name}/config"
    
    def discover(self, mqtt, device_payload, state_topic):
        # need a separate discovery for each value a sensor can return
        for subsensor in self.signature:
            print(f"discovering for subsensor {subsensor}")
            sig = self.signature[subsensor]
            
            icon = sig.get("icon", None)
            unit = sig.get("unit", None)
            
            payload = self.discovery_payload(subsensor, icon, unit)
            
            payload["device"] = device_payload
                
            payload["state_topic"] = state_topic

            extra_topics = ["command_topic",
                            "payload_on",
                            "payload_off",
                            "on_command_type",
                            "hs_command_topic",
                            "hs_state_topic",
                            "hs_value_template",
                            "rgb_command_topic",
                            "rgb_state_topic",
                            "rgb_value_template,"
                            "brightness_command_topic",
                            "brightness_state_topic",
                            "brightness_value_template",
                            ]

            for topic in extra_topics:
                addition = getattr(self, topic, None)

                if addition is None:
                    continue

                print(f"adding extra data at {topic}: {addition}")

                payload[topic] = addition
            
            discovery_topic = self.discovery_topic(subsensor)
            
            print(f"discovering on topic {discovery_topic}")
            print(f"sending payload: {json.dumps(payload)}")
            mqtt.publish(discovery_topic, json.dumps(payload), retain=True)

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
    
    def discovery_payload(self, name, icon, unit) -> dict:
        """
        Generates a dict to send for discovery
        
        args:
            name (str):
                subsensor name as specified by signature
            icon (str):
                mdi icon code
            unit (str):
                measurement unit
                
        returns:
            dict:
                discovery payload
        """
        payload = {}
        # not the right way to do it, but something about pylance hates a direct setup
        payload["unique_id"] = f"{self.parent_uid}_{self.name}_{name}"
        payload["icon"] = icon
        payload["force_update"] = True
        payload["name"] = f"{self.name}_{name}"
                    
        if unit is not None:
            payload["unit_of_measurement"] = unit
            payload["value_template"] = "{{ " + f"value_json.{name}" + " | round(2) }}"
        else:
            payload["value_template"] = "{{ " + f"value_json.{name}" + " }}"
            
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
