from flask import Flask
from flask.ext.pymongo import PyMongo
from flask.ext.babel import Babel
from brew.io import TemperatureController
from brew.state import Machine


app = Flask(__name__)
app.config.from_object('brew.settings')

babel = Babel(app)
mongo = PyMongo(app)
controller = TemperatureController(app)
machine = Machine(app, controller)


import brew.views
import brew.rest
