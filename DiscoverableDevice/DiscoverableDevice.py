from DiscoverableDevice.Sensor import Sensor
from DiscoverableDevice.Switch import Switch
from DiscoverableDevice.Trigger import Trigger

from DiscoverableDevice.utils.timestamp import timestamp
from DiscoverableDevice.utils.pins import get_gpio
from DiscoverableDevice.utils.Profile import Profile
from DiscoverableDevice.utils.Status import blink

try:
    from umqtt.simple import MQTTClient, MQTTException
except ImportError:
    import mip
    mip.install("umqtt.simple")
    print("installed umqtt.simple")
    from umqtt.simple import MQTTClient, MQTTException

from machine import unique_id

import ubinascii
import json
import time

__version__ = "0.0.1a"


RETRY_INTERVAL = 5  # time to wait on a failed MQTT interaction before retrying
RETRY_COUNT = 10


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

    def __init__(
        self,
        wlan,
        host: str,
        user: str,
        password: str,
        port: int = 1883,
        name: str = "PicoTest",
        discovery_prefix: str = "homeassistant",
        location: str | None = None,
        interval: int = 5,
    ):
        self._uid = ubinascii.hexlify(unique_id()).decode()

        super().__init__(
            client_id="",
            server=host,
            port=port,
            user=user,
            password=password,
            keepalive=60,
            ssl=False,
        )

        self._wlan = wlan

        self._name = name
        self._location = location

        self._discovery_prefix = discovery_prefix
        self._discovered = False

        self._interval = interval

        # used for last will/birth detection
        self._broker_alive = True
        self._connection_failure_count = 0
        self._read_failure_count = 0

        self._sensors = {}  # sensors by NAME
        self._command_mapping = {}  # maps topic:[switch]
        self._irq_mapping = {}  # maps pin:switch

        ip = constant(
            name="IP",
            value=wlan.ifconfig()[0],
            icon="mdi:ip-network",
        )
        uid = constant(
            name="UID", value=self.uid, icon="mdi:identifier"
        )

        self.add_entity(ip)
        self.add_entity(uid)

        self._data = {}

        self.initial_setup()

    def initial_setup(self):
        """
        Performs some initial setup, connecting and setting the callback
        """
        try:
            print("Attempting to connect to MQTT Broker...", end=" ")
            self.connect()
        except OSError:
            print(f"failure to connect, waiting {RETRY_INTERVAL}s and retrying.")
            blink(RETRY_INTERVAL)

            self.initial_setup()        
        print("Success!")

        self.cb = self.callback

        statustopic = "homeassistant/status"
        print(f"subscribing to status topic {statustopic}")
        self.subscribe(statustopic)

    def callback(self, topic, msg):
        """
        Callback function that gets called when awaiting a message.

        Switch toggles from HA MQTT are either b'ON' or b'OFF', on the
        topic that was set in that switch's command_topic
        """
        topic = topic.decode()
        msg = msg.decode()

        print(f"received msg '{msg}'\non topic '{topic}'")

        if msg == "online":
            print("Broker reports that it is online")
            if not self.broker_alive:
                print("Broker currently offline, setting up.")
                self.initial_setup()
                self.discover()

            self._broker_alive = True

        elif msg == "offline":
            print("Broker reports that it is going offline")
            self._broker_alive = False
        
        if topic not in self._command_mapping:
            print(f"topic {topic} is not assigned to a sensor, skipping.")
            return
        # list of sensors subscribed to this topic
        sensornames = self._command_mapping[topic]

        for name in sensornames:
            self._sensors[name].callback(msg)

        self.push_data(self.read_sensors(sensornames))

    def irq_callback(self, pin):
        pin = get_gpio(pin)
        print(f"Toplevel irq_callback for pin {pin}")
        name = self._irq_mapping[pin]

        # TODO: fix this, it's horrible
        self.push_data(self.read_sensors())
        self.push_data(self.read_sensors())

    @property
    def wlan(self):
        return self._wlan

    @property
    def broker_alive(self):
        return self._broker_alive

    @property
    def conn_fail_count(self):
        return self._connection_failure_count

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
            sensor.discover(self, self.device_payload)

        for topic in self._command_mapping:
            print("subscribing to command topic", topic)
            self.subscribe(topic)

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
        return [s for s in self._sensors.values()]

    @property
    def switches(self):
        """Returns just switches"""
        return [s for s in self.sensors if isinstance(s, Switch)]

    @property
    def discovery_prefix(self):
        return self._discovery_prefix
    
    def add_entity(self, entity):
        if self.discovered:
            raise RuntimeError("Cannot add entity after discovery")

        name = entity.name
        if name in self.sensors:
            raise ValueError(
                f"Sensor {name} already exists! Delete it or choose a different name."
            )

        entity._discovery_prefix = self.discovery_prefix
        entity._parent_uid = self.uid

        self._sensors[name] = entity

        if isinstance(entity, Trigger):
            # set irq callback
            print(f"setting irq callback for {entity}")
            entity.set_callback(self.irq_callback)
            self._irq_mapping[entity.gpio_pin] = entity.name

        if not hasattr(entity, "command_topic"):
            return

        command_topics = [entity.command_topic]

        for topic in command_topics:            
            try:
                if entity.name not in self._command_mapping[topic]:
                    self._command_mapping[topic].append(entity.name)
            except KeyError:
                self._command_mapping[topic] = [entity.name]

    def delete(self):
        """
        Deletes all sensors
        """
        for sensor in self.sensors:
            topic = sensor.discovery_topic

            self.publish(topic, "")

    @property
    def data(self):
        return self._data

    @property
    def interval(self):
        return self._interval

    def read_sensors(self, selection: list | None = None):
        """
        Read all sensor data and send to broker.

        Note that this will call `discover` if not already called.

        This will "freeze" the class in place, blocking further additions.
        """
        if not self.discovered:
            self.discover()

        self._read_failure_count = 0

        # data to send, {topic: {payload}}
        topics = {}

        for sensor in self.sensors:
            if selection is not None and sensor.name not in selection:
                continue

            try:
                val = sensor._read(force=True)
            except NotImplementedError:
                continue

            if val is None:
                continue
            # need access for rgb_state_topic, etc.
            topic = sensor.state_topic
            # update data entity
            self._data.update(val)

            try:
                topics[topic].update(val)
            except KeyError:
                topics[topic] = val

        return topics

    def push_data(self, topics):
        for topic, payload in topics.items():
            print(timestamp(), payload)
            self.publish(topic, json.dumps(payload))

    def run(self, once=False, dry_run=False):
        print(f"running with interval {self.interval}")
        last_read = 0

        while True:
            if self.broker_alive and time.time() >= last_read + self.interval:
                topics = self.read_sensors()
                last_read = time.time()

                if not dry_run:
                    self.push_data(topics)

            try:
                self.check_msg()
            except MQTTException:
                print("MQTTException, reconnecting")
                self.initial_setup()
                self.discover()
            except OSError:
                print("OSError, reconnecting")
                self.initial_setup()
                self.discover()

            time.sleep(0.05)

            if once:
                return

    def publish(self, *args, **kwargs):
        try:
            super().publish(*args, **kwargs)
            self._connection_failure_count = 0
        except OSError:
            print(
                f"failed to publish {self.conn_fail_count} times, retrying in {RETRY_INTERVAL}s"
            )
            self._connection_failure_count += 1

            if self.conn_fail_count > RETRY_COUNT:
                print(
                    f"connection has failed {RETRY_COUNT} times, assuming the broker is dead"
                )
                self._broker_alive = False
                return

            blink(RETRY_INTERVAL)
            self.publish(*args, **kwargs)


class constant(Sensor):
    def __init__(self, name, value, unit=None, icon=None):
        self.unit = unit
        self.icon = icon
        self.value = value

        super().__init__(name)

    @property
    def signature(self):
        return {self.name: {"icon": self.icon, "unit": self.unit}}

    @property
    def value_template(self):
        return "{{ " + f"value_json.{self.name}" + " }}"

    @property
    def extra_discovery_fields(self):
        output = {"entity_category": "diagnostic"}
        if self.unit is not None:
            output["unit"] = unit

        return output

    def read(self):
        return {self.name: self.value}


if __name__ == "__main__":
    from main import main
    main()
