from Sensor import Sensor

from umqtt.simple import MQTTClient, MQTTException

from machine import unique_id

import ubinascii
import json
import time


__version__ = "0.0.5"


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
        
        self.add_sensor("IP", "mdi:ip-network", None, constant, wlan.ifconfig()[0])
        self.add_sensor("UID", "mdi:identifier", None, constant, self.uid)
        
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
        
        # print(f"received msg '{msg}'\non topic '{topic}'")
        payload = {}
        if topic in self._command_topics:
            idx = self._command_topics[topic]
            switch = self._switches[idx]

            if msg == "ON":
                switch.on()
            else:
                switch.off()
            
        #     data = switch.read()
        #     name = switch.names[0]
        #     if isinstance(data, dict):
        #         payload.update(data)
        #     else:
        #         payload[name] = data

        # if len(payload) != 0:
        #     self.publish(self.state_topic, json.dumps(payload))
        
        # seems sending only updated data causes states to become empty
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
            # need a separate discovery for each value a sensor can return
            for topic, payload in sensor.discover().items():         
                payload["device"] = self.device_payload
                    
                payload["state_topic"] = self.state_topic 
                
                print(f"discovering on topic {topic}")
                self.publish(topic, json.dumps(payload), retain=True)
        
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
        
    def add_sensor(self, name: str, icon: str, unit: str | None, _class, *args, **kwargs):
        """
        Add a sensor at name `name`
        
        Args:
            name:
                name for this sensor, must be unique
            icon:
                mdi icon for this sensor
            unit:
                units to use. Can be None
            _class:
                sensor class. Just subclass Sensor and add a read() function, nothing more
        """
        if self.discovered:
            raise RuntimeError("Cannot add sensor after discovery")
        for sensor in self.sensors:
            if name in self.sensors:
                raise ValueError(f"Sensor {name} already exists! Delete it or choose a different name.")
            
        if not icon.startswith("mdi:"):
            icon = "mdi:" + icon

        sensor = _class(*args,
                        **kwargs,
                        names=name,
                        icons=icon,
                        units=unit)
        
        sensor.discovery_prefix = self.discovery_prefix
        sensor.parent_uid = self.uid

        self._sensors[name] = sensor
        
    def add_switch(self, name, _class, *args, **kwargs):
        """
        Just as with add_sensor, add a sensor at name.
        """
        if self.discovered:
            raise RuntimeError("Cannot add switch after discovery")
        if name in self.sensors:
            raise ValueError(f"Switch {name} already exists! Delete it or choose a different name.")
        switch = _class(*args, **kwargs, names=name)
        
        switch.discovery_prefix = self.discovery_prefix
        switch.parent_uid = self.uid
        
        idx = len(self._switches)
        self._switches[idx] = switch
        
        for topic in switch.command_topics:
            
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
            data = sensor.read()

            if isinstance(data, dict):
                payload.update(data)
            else:
                payload[sensor.names[0]] = data
            
        if not dry_run:
            print(payload)  
            self.publish(self.state_topic, json.dumps(payload))
        else:
            print(payload)
            
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
    def __init__(self, value, *args, **kwargs):
        
        self.value = value

        super().__init__(*args, **kwargs)
        
    def read(self):
        return self.value
    
    
if __name__ == "__main__":
    print("boot") 
    import secrets as s
    
    import rp2
    import network
    
    rp2.country('FR')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
        
    print("Connecting\nto WiFi")
    wlan.connect(s.wifi["ssid"], s.wifi["pass"])

    while not wlan.isconnected() and wlan.status() >= 0:
        time.sleep(1)
        
    print("wifi connected")
    
    test = DiscoverableDevice(wlan,
                              host=s.mqtt["host"],
                              user=s.mqtt["user"],
                              password=s.mqtt["pass"],
                              location="Desk")
    
    # adding sensors and switches
    from examples.SensorCPU import CPUTemp
    from examples.SwitchPicoLED import SwitchLED
    
    test.add_sensor("cpu_temp", "mdi:thermometer", "C", CPUTemp)
    test.add_switch("BoardLED", SwitchLED)
    
    # run indefinitely
    test.run()
    