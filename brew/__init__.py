from flask import Flask
from flask.ext.pymongo import PyMongo

app = Flask(__name__)
app.config.from_object('brew.settings')

mongo = PyMongo(app)

import brew.views
import brew.rest
