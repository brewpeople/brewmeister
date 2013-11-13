from flask import Flask

app = Flask(__name__)
app.config.from_object('brew.settings')

import brew.views
import brew.rest
