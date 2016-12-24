import time

class Dummy(object):

    SLOPE = 5 / 60.0

    def __init__(self, app):
        self.target = 20.0
        self.heating = False
        self.stirring = False
        self._last_temperature = 20.0
        self._last_time = time.time()

    @property
    def temperature(self):
        current_time = time.time()
        elapsed = current_time - self._last_time
        self._last_time = current_time

        # Okay, this is the worst controller *ever*
        if self._last_temperature > self.target:
            self._last_temperature -= elapsed * self.SLOPE
        else:
            self._last_temperature += elapsed * self.SLOPE

        return self._last_temperature
