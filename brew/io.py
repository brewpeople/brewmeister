import datetime
import random
import serial
import struct


COMMAND_GET = 0xf0
COMMAND_SET = 0xf1
COMMAND_STATUS = 0xf2

DS18B20 = 0xf1
HEATER = 0xf2
MOTOR = 0xf3


def TemperatureController(app):
    controller_type = app.config.get('BREW_CONTROLLER_TYPE', 'dummy')

    if controller_type == 'arduino':
        return ArduinoController(app)
    elif controller_type == 'dummy':
        return DummyController(app)

    raise ValueError("Unknown controller type")


class ArduinoController(object):

    def __init__(self, app, connection=None):
        filename = app.config.get('BREW_CONTROLLER_ARDUINO_DEVICE', '/dev/ttyUSB0')
        self.conn = serial.Serial(filename)

    def get_temperature(self):
        self.conn.write(struct.pack('B', COMMAND_GET))
        self.conn.write(struct.pack('B', DS18B20))
        temp = struct.unpack('f', self.conn.read(4))[0]
        return temp

    def set_temperature(self, temperature):
        self.conn.write(struct.pack('B', COMMAND_SET))
        self.conn.write(struct.pack('B', DS18B20))
        self.conn.write(struct.pack('f', temperature))


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

    def get_temperature(self):
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

        return self._last_temperature

    def set_temperature(self, temperature):
        self._set_temperature = temperature
