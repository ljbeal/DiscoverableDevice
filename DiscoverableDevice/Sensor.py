import json
from time import ticks_ms, ticks_diff

class Sensor:

    def __init__(self, name):

        if " " in name:
            raise ValueError("names cannot contain spaces")
        
        self._name = name
        self._data = {}
        self._last_read = 0
        
        self.integration = "sensor"
    
    @property
    def name(self):
        return self._name

    @property
    def parent_uid(self):
        """Parent UID, set by parent on assignment"""
        return self._parent_uid
    
    @property
    def discovery_prefix(self):
        """Parent discovery topic, set by parent on assignment"""
        return self._discovery_prefix

    @property
    def base_topic(self):
        return f"{self._discovery_prefix}/{self.integration}/{self.parent_uid}"

    @property
    def state_topic(self):
        return f"{self.base_topic}/state"    
        
    def discovery_topic(self, subsensor=None):
        if subsensor is None:
            name = self.name
        else:
            name = f"{self.name}_{subsensor}"
            
        return f"{self.base_topic}/{name}/config"
    
    def discover(self, mqtt, device_payload):
        # need a separate discovery for each value a sensor can return
        for subsensor in self.signature:
            print(f"discovering for subsensor {subsensor}")
            signature_data = self.signature[subsensor]
                        
            payload = {"unique_id": f"{self.parent_uid}_{self.name}_{subsensor}",
                       "force_update": True,
                       "device": device_payload,
                       "state_topic": self.state_topic}

            if len(self.signature) == 1:
                payload["name"] = subsensor
            else:
                payload["name"] = f"{self.name}_{subsensor}"

            unit = signature_data.get("unit", None)
            if unit is not None:
                payload["unit_of_measurement"] = unit

            icon = signature_data.get("icon", None)
            if icon is not None:
                payload["icon"] = icon

            if hasattr(self, "value_template"):
                try:
                    vt = self.value_template
                    print("value template set by direct property")
                except TypeError:
                    vt = self.value_template(subsensor)
                    print("value template set by function call")

            else:
                vt = "{{ " + f"value_json.{subsensor}" 

                if "value_mod" in signature_data:
                    value_mod = signature_data["value_mod"]
                    vt += f" | {value_mod}"
                
                vt += " }}"
                print("value template set by signature extraction")

            try:
                if vt is not None:
                    payload["value_template"] = vt
                    print(f"value template set to {vt}")
            except NameError:
                raise RuntimeError(f"No Value Template found for {subsensor}")

            if hasattr(self, "command_topic"):
                payload["command_topic"] = self.command_topic

            if hasattr(self, "extra_discovery_fields"):
                for topic, value in self.extra_discovery_fields.items():

                    print(f"adding extra data at {topic}: {value}")

                    payload[topic] = value

            if len(self.signature) == 1:
                discovery_topic = self.discovery_topic()
            else:
                discovery_topic = self.discovery_topic(subsensor)
            
            print(f"discovering on topic {discovery_topic}")
            print(f"sending payload: {json.dumps(payload)}")
            mqtt.publish(discovery_topic, json.dumps(payload), retain=True)
    
    @property
    def signature(self) -> dict:
        raise NotImplementedError
        
    def read(self) -> dict:
        raise NotImplementedError
    
    def _read(self, interval: int = 5, force: bool = False):
        if not force and not ticks_diff(ticks_ms(), self._last_read) > interval * 1000:
            return

        self._last_read = ticks_ms()
        self._data = self.read()

        return self.data

    @property
    def data(self):
        return self._data
    

def ensure_list(input) -> list:
    """Attempt to coerce `input` to list type"""
    if isinstance(input, list):
        return input
    return [input]


if __name__ == "__main__":
    test = Sensor(name="test")

