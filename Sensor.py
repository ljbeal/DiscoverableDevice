class Sensor:
    def __init__(self, name, icon, unit):
        
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
    def parent_uid(self):
        return self._parent_uid
    
    @parent_uid.setter
    def parent_iud(self, uid):
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
    
    @property
    def discovery_payload(self):
        payload = {"unique_id": f"{self.parent_uid}_{self.name}",
                   "icon": self.icon,
                   "force_update": True,
                   "name": self.name
                   }
                
        if self.unit is not None:
            payload["unit_of_measurement"] = self.unit
            payload["value_template"] = "{{ " + f"value_json.{self.name}" + " | round(2) }}"
        else:
            payload["value_template"] = "{{ " + f"value_json.{self.name}" + " }}"
                   
        return payload
        
    def read(self):
        raise NotImplementedError
        