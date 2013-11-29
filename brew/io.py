import datetime
import random


class TemperatureController(object):
    def __init__(self, app):
        controller_type = 'dummy'

        if 'BREW_CONTROLLER_TYPE' in app.config:
            controller_type = app.config['BREW_CONTROLLER_TYPE']

        if controller_type == 'arduino':
            filename = '/dev/ttyUSB0'

            if 'BREW_CONTROLLER_ARDUINO_DEVICE' in app.config:
                filename = app.config['BREW_CONTROLLER_ARDUINO_DEVICE']

            self._real_controller = ArduinoController(filename)
        elif controller_type == 'dummy':
            slope = 2.0

            if 'BREW_CONTROLLER_DUMMY_SLOPE' in app.config:
                slope = float(app.config['BREW_CONTROLLER_DUMMY_SLOPE'])

            self._real_controller = DummyController(slope)

    def get_temperature(self):
        return self._real_controller.get_temperature()

    def set_temperature(self, temperature):
        self._real_controller.set_temperature(temperature)


class ArduinoController(TemperatureController):
    def __init__(self, filename):
        self._filename = filename

    def get_temperature(self):
        with open(self._filename, 'r') as f:
            return f.read()

    def set_temperature(self, temperature):
        with open(self._filename, 'w') as f:
            f.write(str(temperature))


class DummyController(TemperatureController):
    def __init__(self, slope, current_temperature=20.0):
        """Create a new dummy controller with a given temperature slope in
        degree celsius per minute and a current temperature in degree
        celsius."""
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
