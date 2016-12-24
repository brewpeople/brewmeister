from flask import Flask
from flask_restful import Api
from brewmeister.controller import Dummy

app = Flask(__name__)
app.secret_key = 'x6TbAJ5QLWPtDtElwDpZu64XjvcrVV_w'

app.config['DEBUG'] = True

controller = Dummy(app)

from brewmeister.resources import Temperature, Heating, Stirrer, Timer

api = Api(app)
api.add_resource(Temperature, '/api/v1/temperature')
api.add_resource(Heating, '/api/v1/heating')
api.add_resource(Stirrer, '/api/v1/stirrer')
api.add_resource(Timer, '/api/v1/timer')

import brewmeister.views
