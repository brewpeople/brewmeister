import datetime
import random
import serial
import struct


def TemperatureController(app):
    controller_type = app.config.get('BREW_CONTROLLER_TYPE', 'dummy')
    app.logger.info("Using {} controller".format(controller_type))

    if controller_type == 'arduino':
        return ArduinoController(app)
    elif controller_type == 'dummy':
        return DummyController(app)

    raise ValueError("Unknown controller type")


class ArduinoConnection(object):
    """Low-level communication interface to the Arduino."""
    def __init__(self, filename):
        self.conn = serial.Serial(filename)

    def write(self, data):
        self.conn.write(data)

    def read(self, n_bytes):
        return self.conn.read(n_bytes)


class ArduinoController(object):

    COMMAND_SET = 0x0
    COMMAND_GET = 0x1

    INSTRUMENT_TEMPERATURE = 0x0

    TYPE_DECIMAL = 0x0
    TYPE_STRING = 0x1
    TYPE_BOOLEAN = 0x3

    STATUS_OK = 0x0

    set_map = {
        INSTRUMENT_TEMPERATURE: TYPE_DECIMAL
    }

    def __init__(self, app, connection=None):
        filename = app.config.get('BREW_CONTROLLER_ARDUINO_DEVICE', '/dev/ttyUSB0')
        self.conn = connection if connection else ArduinoConnection(filename)

    def write_command(self, cmd):
        self.conn.write(struct.pack('B', cmd))

        reply = struct.unpack('B', self.conn.read(1))
        status = reply >> 2

        if status != STATUS_OK:
            raise Exception("Problem reading {}".format(instrument))

        return reply

    def get(self, instrument):
        cmd = (COMMAND_GET << 6) & (instrument << 2)
        reply = self.write_command(cmd)

    def set(self, instrument, value):
        dtype = set_map[instrument]
        cmd = (COMMAND_SET << 6) & (instrument << 2) & dtype
        self.write_command(cmd)

    def get_temperature(self):
        return self.get(INSTRUMENT_TEMPERATURE)

    def set_temperature(self, temperature):
        self.set(INSTRUMENT_TEMPERATURE, temperature)


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
