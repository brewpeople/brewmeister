import re
import time
import threading
import RPi.GPIO as gpio
from flask import Flask, request
from flask_restful import Api, Resource, abort

app = Flask(__name__)
app.secret_key = 'x6TbAJ5QLWPtDtElwDpZu64XjvcrVV_w'
app.config['DEBUG'] = True

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


sensors = {
    'wort': Sensor('28-00000542d319'),
    'manual': Sensor('28-000009b7f883'),
}


switches = {
    'stirrer': GPIOSwitch(5),
}


states = {
    'valve': GPIOState(6),
    'stirrer': switches['stirrer'],
}


def read_sensors():
    while True:
        for sensor in sensors.values():
            sensor.read_temperature()

        time.sleep(1)


read_sensors_thread = threading.Thread(target=read_sensors)
read_sensors_thread.start()


class Temperature(Resource):
    def get(self, name):
        if name not in sensors:
            abort(404, message="Sensor {} not found".format(name))

        return dict(temperature=sensors[name].temperature)


class Switch(Resource):
    def put(self, name):
        if name not in switches:
            abort(404, message="Switch {} not found".format(name))

        data = request.get_json()

        if data and 'on' in data:
            switches[name].switch(data['on'])
        else:
            abort(400, message="No or wrong payload")


class State(Resource):
    def get(self, name):
        if name not in states:
            abort(404, message="State {} not found".format(name))

        return dict(state=states[name].state)


api = Api(app)
api.add_resource(Temperature, '/temp/<string:name>')
api.add_resource(Switch, '/switch/<string:name>')
api.add_resource(State, '/state/<string:name>')
