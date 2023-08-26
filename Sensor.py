class Sensor:
    def __init__(self, name, icon, unit, parent_uid):
        
        if " " in name:
            raise ValueError("names cannot contain spaces")
        
        self._name = name
        self._icon = icon
        self._unit = unit
        
        self._parent_uid = parent_uid
        
    @property
    def integration(self):
        return "sensor"
    
    @property
    def name(self):
        return self._name
    
    @property
    def icon(self):
        return self._icon
    
    @property
    def parent_uid(self):
        return self._parent_uid
    
    @property
    def unit(self):
        return self._unit
    
    @property
    def function(self):
        return self._function
    
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
        