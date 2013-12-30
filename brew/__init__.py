import time
from flask import Flask
from flask.ext.pymongo import PyMongo
from flask.ext.babel import Babel
from flask.ext.cache import Cache
from bson.objectid import ObjectId
from brew.io import TemperatureController, Monitor
from brew.state import Machine


app = Flask(__name__)
app.config.from_object('brew.settings')
app.config.from_pyfile('brewmeister.cfg', silent=True)

babel = Babel(app)
cache = Cache(app)
mongo = PyMongo(app)
controller = TemperatureController(app)
machine = Machine(app, controller)


def record_temperature(brew_id, temperature):
    with app.app_context():
        now = time.time()
        query = {'_id': ObjectId(brew_id)}
        op = {'$push': {'temperatures': (now, temperature)}}

        mongo.db.brews.update(query, op)


monitor = Monitor(controller, record_temperature, timeout=2)


import brew.views
import brew.rest
