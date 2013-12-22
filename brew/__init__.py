from flask import Flask
from flask.ext.pymongo import PyMongo
from flask.ext.babel import Babel
from flask.ext.cache import Cache
from brew.io import TemperatureController
from brew.state import Machine


app = Flask(__name__)
app.config.from_object('brew.settings')
app.config.from_pyfile('brewmeister.cfg', silent=True)

babel = Babel(app)
cache = Cache(app)
mongo = PyMongo(app)
controller = TemperatureController(app)
machine = Machine(app, controller)


import brew.views
import brew.rest
