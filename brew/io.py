import datetime
import random
import serial
import struct


COMMAND_GET = 0xf0
COMMAND_SET = 0xf1

DS18B20 = 0xf1
HEATER = 0xf2
STIRRER = 0xf3


def TemperatureController(app):
    controller_type = app.config.get('BREW_CONTROLLER_TYPE', 'dummy')

    if controller_type == 'arduino':
        return ArduinoController(app)
    elif controller_type == 'dummy':
        return DummyController(app)

    raise ValueError("Unknown controller type")


class ArduinoController(object):

    def __init__(self, app, connection=None):
        self.filename = app.config.get('BREW_CONTROLLER_ARDUINO_DEVICE', '/dev/ttyUSB0')
        self.status = None
        self.reconnect()

    @property
    def connected(self):
        return self.conn != None

    def reconnect(self):
        try:
            self.conn = serial.Serial(self.filename)
        except OSError as exception:
            self.conn = None
            self.status = str(exception)

    def send_header(self, command, device):
        self.conn.write(struct.pack('B', command))
        self.conn.write(struct.pack('B', device))

    def write_boolean(self, device, value):
        if self.connected:
            self.send_header(COMMAND_SET, device)
            self.conn.write(struct.pack('?', value))

    def read_boolean(self, device):
        if self.connected:
            self.send_header(COMMAND_GET, device)
            return struct.unpack('?', self.conn.read(1))[0]

    def write_float(self, device, value):
        if self.connected:
            self.send_header(COMMAND_SET, device)
            self.conn.write(struct.pack('f', value))

    def read_float(self, device):
        if self.connected:
            self.send_header(COMMAND_GET, device)
            return struct.unpack('f', self.conn.read(4))[0]

    @property
    def temperature(self):
        if not self.connected:
            return 0.0

        return self.read_float(DS18B20)

    def set_reference_temperature(self, temperature):
        self.write_float(DS18B20, temperature)

    @property
    def heating(self):
        return self.read_boolean(HEATER)

    @heating.setter
    def heating(self, value):
        self.write_boolean(HEATER, value)

    @property
    def stirring(self):
        return self.read_boolean(STIRRER)

    @stirring.setter
    def stirring(self, value):
        self.write_boolean(STIRRER, value)


class DummyController(object):
    def __init__(self, app, current_temperature=20.0):
        """Create a new dummy controller with a given temperature slope in
        degree celsius per minute and a current temperature in degree
        celsius."""
        slope = 2.0

        if 'BREW_CONTROLLER_DUMMY_SLOPE' in app.config:
            slope = float(app.config['BREW_CONTROLLER_DUMMY_SLOPE'])

        # Adjust the slope to degree per sec
        self._slope = slope / 60.0
        self._set_temperature = current_temperature
        self._last_temperature = current_temperature
        self._last_time = datetime.datetime.now()

        self.heating = False
        self.stirring = False

    @property
    def connected(self):
        return True

    def reconnect(self):
        pass

    @property
    def temperature(self):
        current_time = datetime.datetime.now()
        elapsed = (current_time - self._last_time).total_seconds()
        self._last_time = current_time

        if abs(self._last_temperature - self._set_temperature) < 0.1:
            return self._last_temperature

        increase = elapsed * self._slope

        # add some noise
        increase += random.gauss(0.5, 0.1)

        # Okay, this is the worst controller *ever*
        if self._last_temperature > self._set_temperature:
            self._last_temperature -= elapsed * self._slope
        else:
            self._last_temperature += elapsed * self._slope

        self.heating = abs(self._last_temperature - self._set_temperature) > 0.5
        self.stirring = self.heating

        return self._last_temperature

    def set_reference_temperature(self, temperature):
        self._set_temperature = temperature
