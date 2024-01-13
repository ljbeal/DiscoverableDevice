from .Sensor import Sensor

from umqtt.simple import MQTTClient, MQTTException

from machine import unique_id

import ubinascii
import json
import time

__version__ = "0.1.1"


class DiscoverableDevice(MQTTClient):
    """
    Base class for a device which communicates with HA via MQTT
    
    Args:
        host:
            mqtt broker hostname, either address or ip
        user:
            mqtt username
        password:
            mqtt password
        port:
            mqtt broker port
        name:
            device name
        discovery_prefix:
            home assistant discovery prefix, defaults to "homeassistant"
        location:
            device location, defaults None, and will be unreported
        interval:
            report interval, defaults to 5s
    """
    
    def __init__(self,
                 wlan,
                 host: str,
                 user: str,
                 password: str,
                 port: int = 1883,
                 name: str = "PicoTest",
                 discovery_prefix: str = "homeassistant",
                 location: str | None = None,
                 interval: int = 5):
        
        self._uid = ubinascii.hexlify(unique_id()).decode()
        
        super().__init__(client_id="",
                         server=host,
                         port=port,
                         user=user,
                         password=password,
                         keepalive=60,
                         ssl=False)
        
        self._name = name
        self._location = location
        
        self._discovery_prefix = discovery_prefix
        self._discovered = False
        
        self._interval = interval
        
        self._sensors = {}  # sensors by NAME
        self._switches = {}  # switches by ID
        self._command_topics = {}  # switch TOPIC -> ID link
        
        ip = constant(name="Network", subname="IP", value=wlan.ifconfig()[0], icon="mdi:ip-network")
        uid = constant(name="Device", subname="UID", value=self.uid, icon="mdi:identifier")

        self.add_sensor(ip)
        self.add_sensor(uid)
        
        self._data = {}
        
        self.setup()
        
    def setup(self):
        """
        Performs some initial setup, connecting and setting the callback
        """
        self.connect()
        
        self.cb = self.callback
        
        self.subscribe(b"cmdtest")
            
    def callback(self, topic, msg):
        """
        Callback function that gets called when awaiting a message.
        
        Switch toggles from HA MQTT are either b'ON' or b'OFF', on the
        topic that was set in that switch's command_topic
        """
        topic = topic.decode()
        msg = msg.decode()
        
        print(f"received msg '{msg}'\non topic '{topic}'")
        payload = {}
        if topic in self._command_topics:
            idx = self._command_topics[topic]
            switch = self._switches[idx]
            
            switch.callback(msg)

        self.read_sensors()

    @property
    def state_topic(self):
        return f"{self._discovery_prefix}/sensor/{self.uid}/state"    
    
    @property
    def device_payload(self):
        """Device payload for nicer looking interface in HA"""
        payload = {}
        # not the right way to do it, but something about pylance hates a direct setup
        payload["identifiers"] = [self.uid]
        payload["name"] = self.name
        payload["sw_version"] = __version__
        payload["model"] = self.name
        payload["manufacturer"] = "ljbeal"
        
        if self.location is not None:
            payload["suggested_area"] = self.location

        return payload 
        
    def discover(self):
        """
        Iterate over all sensors and switches, sending their discovery payload to their discovery address
        """
        for sensor in self.sensors:
            print(f"discovering for sensor {sensor}")
            sensor.discover(self, self.device_payload, self.state_topic)
        
        self._discovered = True
                
    @property
    def discovered(self):
        """Have we run the discovery process?"""
        return self._discovered
        
    @property
    def name(self):
        return self._name
    
    @property
    def location(self):
        return self._location
    
    @location.setter
    def location(self, location):
        self._location = location
        
    @property
    def uid(self):
        return self._uid
        
    @property
    def sensors(self):
        """Returns all sensors and switches"""
        tmp = [sensor for sensor in self._sensors.values()]
        tmp += [sensor for sensor in self._switches.values()]
        return tmp
    
    @property
    def switches(self):
        """Returns just switches"""
        return list(self._switches.values())
    
    @property
    def discovery_prefix(self):
        return self._discovery_prefix
        
    def add_sensor(self,
                   sensor):
        """
        Add a sensor `sensor`
        
        Args:
            sensor:
                sensor to store
        """
        if self.discovered:
            raise RuntimeError("Cannot add sensor after discovery")
        
        name = sensor.name
        if name in self.sensors:
            raise ValueError(f"Sensor {name} already exists! Delete it or choose a different name.")
        
        sensor.discovery_prefix = self.discovery_prefix
        sensor.parent_uid = self.uid

        self._sensors[name] = sensor
        
    def add_switch(self, switch):
        """
        Just as with add_sensor, add a switch.
        """
        if self.discovered:
            raise RuntimeError("Cannot add switch after discovery")
        
        name = switch.name
        if name in self.sensors:
            raise ValueError(f"Switch {name} already exists! Delete it or choose a different name.")
        
        switch.discovery_prefix = self.discovery_prefix
        switch.parent_uid = self.uid
        
        idx = len(self._switches)
        self._switches[idx] = switch
        
        topic = switch.command_topic
        self._command_topics[topic] = idx
        print("subscribing to command topic", topic)
        self.subscribe(topic)
        
    def delete(self):
        """
        Deletes all sensors
        """
        for sensor in self.sensors:
            topic = sensor.discovery_topic
            
            self.publish(topic, "")
        
    def read_sensors(self, dry_run=False):
        """
        Read all sensor data and send to broker.
        
        Note that this will call `discover` if not already called.
        
        This will "freeze" the class in place, blocking further additions.
        """
        if not self.discovered:
            self.discover()
        
        # data to send, {topic: {payload}}
        payload = {}
        for sensor in self.sensors:
            val = sensor.read()

            payload.update(val)
            
        if not dry_run:
            print(payload)  
            self.publish(self.state_topic, json.dumps(payload))
        else:
            print(payload)
            
        self._data = payload
            
    @property
    def data(self):
        return self._data
            
    @property
    def interval(self):
        return self._interval
            
    def run(self):
        print(f"running with interval {self.interval}")
        
        last_read = 0
        
        def read():
            self.read_sensors(dry_run=False)            
        
        while True:
            if time.time() > last_read + self.interval:
                read()
                
                last_read = time.time()
            
            try:
                self.check_msg()
            except MQTTException:
                print("MQTTException, reconnecting")
                self.setup()
            except OSError:
                print("OSError, reconnecting")
                self.setup()

            time.sleep(0.05)
            

class constant(Sensor):
    def __init__(self, name, value, subname=None, unit=None, icon=None):
        
        self.unit = unit
        self.icon = icon
        self.value = value
        
        self.displayname = subname or name

        super().__init__(name)
    
    @property
    def signature(self):
        return {self.displayname: {"icon": self.icon,
                                   "unit": self.unit}
                }
        
    def read(self):
        return {self.displayname: self.value}
