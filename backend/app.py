from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from glob import glob
import json
import requests

import random

app = Flask(__name__)
CORS(app)

def read_recipe_file(fn):
    fh = open(fn, 'r')
    return json.load(fh)

def _proxy(*args, **kwargs):
    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, 'http://192.168.0.180:5000/'),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response

@app.route('/control/<path:path>', methods=['POST', 'GET', 'PUT'])
def catchall(*args, **kwargs):
    return _proxy(*args, **kwargs)


@app.route('/recipes')
def recipes():
    recipe_files = glob('./recipes/*.json')
    recipes = [read_recipe_file(f) for f in recipe_files]
    return jsonify(recipes)

@app.route('/process/info')
def process_info():
    process = {
        "recipe": "weizenbock",
        "readings": {
            "flame": True,
            "temperature": random.random() * 3 + 65,
            "stirr": True
        },
        "stages": [
            {
                "started": "2019-01-26T16:32:57.475Z",
                "finished": "2019-01-26T17:32:57.475Z",
                "name": "setup process"
            },
            {
                "started": "2019-01-26T18:32:57.475Z",
                "finished": "2019-01-26T19:32:57.475Z",
                "name": "heat to 65°C"
            },
            {
                "started": "2019-01-26T19:32:57.475Z",
                "finished": "2019-01-26T20:32:57.475Z",
                "name": "hold 65°C"
            },   
             {
                "started": "2019-01-26T20:32:57.475Z",
                "finished": "2019-01-26T21:32:57.475Z",
                "name": "heat 72°C"
            },  
             {
                "started": "2019-01-26T19:32:57.475Z",
                "name": "hold 72°C"
            },
            {
                "name": "lautering"
            }        
        ]
    }

    return jsonify(process)