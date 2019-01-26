import time
import datetime
import threading
from .hardware import Sensor, GPIOSwitch
from flask import Flask, request
from flask_restful import Api, Resource, abort

app = Flask(__name__)
app.secret_key = 'x6TbAJ5QLWPtDtElwDpZu64XjvcrVV_w'
app.config['DEBUG'] = True


class HardwareState(object):
    def __init__(self):
        self.sensors = {
            'wort': Sensor('28-00000542d319'),
            'manual': Sensor('28-000009b7f883'),
        }

        self.switches = {
            'stirrer': GPIOSwitch(5),
        }

        self.confirm = False
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    @property
    def wort_sensor(self):
        return self.sensors['wort']

    def run(self):
        while True:
            for sensor in self.sensors.values():
                sensor.read_temperature()

            time.sleep(1)


class Stage(object):
    def __init__(self):
        print("Constructor {}".format(self))
        self.entered = None

    def enter(self):
        self.entered = datetime.datetime.now()
        print("{} enter at {}".format(self, self.entered))

    def exit(self):
        now = datetime.datetime.now()
        print("{} exit at {}".format(self, now))

    def complete(self, state):
        raise NotImplementedError


class Confirmation(Stage):
    def complete(self, state):
        r = state.confirm
        state.confirm = False
        return r

    def __repr__(self):
        return '<Stage:Confirm>'


class Wait(Stage):
    def __init__(self, duration):
        self.duration = duration

    def complete(self, state):
        now = datetime.datetime.now()
        return now >= self.entered + self.duration

    def __repr__(self):
        return '<Stage:Wait({})>'.format(self.duration)


class TemperatureReached(Stage):
    def __init__(self, temperature):
        self.temperature = temperature

    def complete(self, state):
        # control gas
        print("{} >= {}".format(state.wort_sensor.temperature, self.temperature))
        return state.wort_sensor.temperature >= self.temperature

    def __repr__(self):
        return '<Stage:Reached({} degC)>'.format(self.temperature)


class Brew(object):
    def __init__(self, stages, state):
        self.stages = stages
        self.state = state
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        self.current_stage = 0

    def run(self):
        for i, stage in enumerate(self.stages):
            stage.enter()
            self.current_stage = i

            while not stage.complete(self.state):
                time.sleep(1)

            stage.exit()


brews = []
state = HardwareState()


class BrewControl(Resource):
    def post(self):
        stages = [
            Confirmation(),
            Wait(datetime.timedelta(seconds=5)),
            TemperatureReached(19.0),
        ]

        brew_id = len(brews)
        brews.append(Brew(stages, state))
        return dict(id=brew_id)


class BrewInteraction(Resource):
    def put(self, brew_id):
        brew = brews[brew_id]
        brew.state.confirm = True

    def get(self, brew_id):
        brew = brews[brew_id]
        return dict(stage=brew.current_stage)


class Temperature(Resource):
    def get(self):
        return {k: v.temperature for k, v in state.sensors.items()}


api = Api(app)
api.add_resource(Temperature, '/temp')
api.add_resource(BrewControl, '/brew')
api.add_resource(BrewInteraction, '/brew/<int:brew_id>')
