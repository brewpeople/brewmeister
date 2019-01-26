import re
import time
import threading
import RPi.GPIO as gpio


gpio.setmode(gpio.BCM)


class Sensor(object):
    def __init__(self, device):
        self.path = '/sys/bus/w1/devices/{}/w1_slave'.format(device)
        self.temperature = 18.0
        self.pattern = re.compile(r't=(\d+)')

    def read_temperature(self):
        with open(self.path, 'r') as fp:
            data = fp.read()

            if not data:
                return

            match = self.pattern.search(data)

            if match:
                self.temperature = float(match.group(1).strip()) / 1000


class GPIOSwitch(object):
    def __init__(self, pin):
        gpio.setup(pin, gpio.OUT, initial=gpio.HIGH)
        self.pin = pin
        self.state = False

    def switch(self, on):
        gpio.output(self.pin, gpio.LOW if on else gpio.HIGH)
        self.state = on


class GPIOState(object):
    def __init__(self, pin):
        gpio.setup(pin, gpio.IN)
        self.pin = pin

    @property
    def state(self):
        return gpio.input(self.pin) == gpio.LOW
