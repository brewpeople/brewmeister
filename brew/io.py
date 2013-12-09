import datetime
import random


def TemperatureController(app):
    controller_type = app.config.get('BREW_CONTROLLER_TYPE', 'dummy')
    app.logger.info("Using {} controller".format(controller_type))

    if controller_type == 'arduino':
        return ArduinoController(app)
    elif controller_type == 'dummy':
        return DummyController(app)

    raise ValueError("Unknown controller type")


class ArduinoController(object):
    def __init__(self, app):
        self._filename = app.config.get('BREW_CONTROLLER_ARDUINO_DEVICE', '/dev/ttyUSB0')

    def get_temperature(self):
        with open(self._filename, 'r') as f:
            return f.read()

    def set_temperature(self, temperature):
        with open(self._filename, 'w') as f:
            f.write(str(temperature))


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
