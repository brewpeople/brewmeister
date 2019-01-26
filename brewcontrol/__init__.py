import time
import datetime
import threading
from .hardware import Sensor, GPIOSwitch, GPIOState
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

        self.states = {
            'valve': GPIOState(6),
            'stirrer': self.switches['stirrer'],
        }

        self.confirm = False
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    @property
    def wort_sensor(self):
        return self.sensors['wort']

    @property
    def stirrer(self):
        return self.switches['stirrer']

    def run(self):
        while True:
            for sensor in self.sensors.values():
                sensor.read_temperature()

            time.sleep(1)


class Stage(object):
    def __init__(self, description):
        self.started = None
        self.finished = None
        self.description = description

    def enter(self):
        self.started = datetime.datetime.now()
        print("{} enter at {}".format(self, self.started))

    def exit(self):
        self.finished = datetime.datetime.now()
        print("{} exit at {}".format(self, self.finished))

    def complete(self, state):
        raise NotImplementedError


class Setup(Stage):
    def __init__(self, description):
        super(Setup, self).__init__(description)

    def complete(self, state):
        state.stirrer.switch(False)
        return True


class Confirmation(Stage):
    def __init__(self, description):
        super(Confirmation, self).__init__(description)

    def complete(self, state):
        r = state.confirm
        state.confirm = False
        return r

    def __repr__(self):
        return '<Stage:Confirm>'


class Wait(Stage):
    def __init__(self, duration, description):
        super(Wait, self).__init__(description)
        self.duration = duration

    def complete(self, state):
        now = datetime.datetime.now()
        return now >= self.started + self.duration

    def __repr__(self):
        return '<Stage:Wait({})>'.format(self.duration)


class TemperatureReached(Stage):
    def __init__(self, temperature, description):
        super(TemperatureReached, self).__init__(description)
        self.temperature = temperature

    def complete(self, state):
        print("{} >= {}".format(state.wort_sensor.temperature, self.temperature))
        reached = state.wort_sensor.temperature >= self.temperature

        if not reached:
            state.stirrer.switch(True)

        return reached

    def __repr__(self):
        return '<Stage:Reached({} degC)>'.format(self.temperature)


class Brew(object):
    def __init__(self, name, stages, state):
        self.name = name
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


class BrewList(Resource):
    def get(self):
        return dict(brews=[i for i,_ in enumerate(brews)])


class BrewControl(Resource):
    def post(self):
        data = request.get_json()

        stages = [
            Setup("Initialize system"),
            Confirmation("Waiting for user input"),
            Wait(datetime.timedelta(seconds=5), "Waiting 5 seconds"),
            TemperatureReached(25.0, "Waiting for temperature to reach 19 C"),
        ]

        brew_id = len(brews)
        brews.append(Brew(data['name'], stages, state))
        return dict(id=brew_id)


class BrewInteraction(Resource):
    def put(self, brew_id):
        if brew_id >= len(brews):
            abort(404, message="Brew does not exist")
        brew = brews[brew_id]
        brew.state.confirm = True
        return {}

    def get(self, brew_id):
        brew = brews[brew_id]
        stages = [dict(started=s.started.isoformat() if s.started else None,
                       finished=s.finished.isoformat() if s.finished else None,
                       name=s.description,
                       needsInteraction=isinstance(s, Confirmation))
                  for s in brew.stages]
        return dict(stages=stages)


class Temperature(Resource):
    def get(self):
        return {k: v.temperature for k, v in state.sensors.items()}


class Switch(Resource):
    def put(self, name):
        if name not in state.switches:
            abort(404, message="Switch not found")

        data = request.get_json()

        if 'on' not in data:
            abort(400, message="Payload wrong")

        state.switches[name].switch(data['on'])


api = Api(app)
api.add_resource(Temperature, '/temperature')
api.add_resource(Switch, '/switch/<string:name>')
api.add_resource(BrewList, '/brews')
api.add_resource(BrewControl, '/brew')
api.add_resource(BrewInteraction, '/brew/<int:brew_id>')
