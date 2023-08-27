class Sensor:
    def __init__(self, 
                 names: str | list, 
                 icons: str | list | None, 
                 units: str | list):
        
        names = ensure_list(names)
        icons = ensure_list(icons)
        units = ensure_list(units)

        if any([" " in name for name in names]):
            raise ValueError("names cannot contain spaces")
        
        self._names = names
        self._icons = icons
        self._units = units
        
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
    def parent_uid(self):
        return self._parent_uid
    
    @parent_uid.setter
    def parent_uid(self, uid):
        self._parent_uid = uid
    
    @property
    def names(self):
        return self._names
    
    @property
    def icons(self):
        return self._icons
    
    @property
    def units(self):
        return self._units
    
    def value_template(self, name):
        return "{{ " + f"value_json.{name}" + " }}"
    
    def discover(self) -> dict:
        """
        Generates a dict of {topic: payload} to send for discovery
        """
        output = {}
        for name, icon, unit in zip(self.names, self.icons, self.units):
            payload = {}
            # not the right way to do it, but something about pylance hates a direct setup
            payload["unique_id"] = f"{self.parent_uid}_{name}"
            payload["icon"] = icon
            payload["force_update"] = True
            payload["name"] = name
                        
            if unit is not None:
                payload["unit_of_measurement"] = unit
                payload["value_template"] = "{{ " + f"value_json.{name}" + " | round(2) }}"
            else:
                payload["value_template"] = "{{ " + f"value_json.{name}" + " }}"

            topic = f"{self._discovery_prefix}/{self.integration}/{self.parent_uid}/{name}/config"

            output[topic] = payload
            
        return output
        
    def read(self):
        raise NotImplementedError
    

def ensure_list(input) -> list:
    """Attempt to coerce `input` to list type"""
    if isinstance(input, list):
        return input
    return [input]


if __name__ == "__main__":
    test = Sensor(names="test", icons=None, units="")
