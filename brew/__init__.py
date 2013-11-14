from flask import Flask
from flask.ext.pymongo import PyMongo
from brew.io import TemperatureController
from brew.state import Machine


app = Flask(__name__)
app.config.from_object('brew.settings')

mongo = PyMongo(app)
controller = TemperatureController(app)
machine = Machine(controller)


import brew.views
import brew.rest
