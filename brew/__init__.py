from flask import Flask

app = Flask(__name__)

import brew.views
import brew.rest
