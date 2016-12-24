import random
import time
from brewmeister import controller
from flask_restful import Resource, reqparse


class Stopwatch(object):

    def __init__(self):
        self.start_time = None

    def reset(self):
        self.start_time = time.time()

    @property
    def elapsed(self):
        if not self.start_time:
            return 0

        return time.time() - self.start_time


timer = Stopwatch()


class Temperature(Resource):
    def get(self):
        return dict(target=controller.target,
                    temperature=controller.temperature)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('target', type=float)
        args = parser.parse_args()
        controller.target = args['target']
        return dict(okay=True), 201


class Heating(Resource):
    def get(self):
        return controller.heating

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('on', type=bool, required=True)
        args = parser.parse_args()
        controller.heating = args['on']
        return dict(okay=True), 201


class Stirrer(Resource):
    def get(self):
        return controller.stirring

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('on', type=bool, required=True)
        args = parser.parse_args()
        controller.stirring = args['on']
        return dict(okay=True), 201


class Timer(Resource):
    def get(self):
        return timer.elapsed

    def post(self):
        timer.reset()
        return dict(okay=True), 201

