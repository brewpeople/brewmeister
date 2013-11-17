import json
import jsonschema
from pkg_resources import resource_string
from flask import request, render_template, jsonify, redirect
from bson.objectid import ObjectId
from brew import app, mongo, controller, machine


@app.route('/')
def index():
    recipes = mongo.db.recipes.find()
    return render_template('index.html', recipes=recipes, machine=machine)


@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    schema_text = resource_string(__name__, 'data/recipe.schema.json').decode('utf-8')

    if request.method == 'POST':
        recipe_json = request.get_json()
        schema = json.loads(schema_text)
        jsonschema.validate(schema, recipe_json)
        mongo.db.recipes.insert(recipe_json)

    return render_template('create.html', schema=schema_text)


@app.route('/brews/prepare/<recipe_id>', methods=['GET'])
def prepare(recipe_id):
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))
    return render_template('prepare.html', recipe=recipe)


@app.route('/brews', methods=['GET', 'POST'])
def brew():
    if request.method == 'POST':
        recipe_id = request.form['recipe_id']
        recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))

        mash = []

        for step in recipe['mash']:
            mash.append(dict(name=step['name'],
                             time=step['time'],
                             temperature=step['temperature'],
                             state='waiting'))

        mash[0]['state'] = 'pending'

        machine.fsm.heat(temperature=mash[0]['temperature'])

    return render_template('brew.html', mash=mash, machine=machine)


@app.route('/brews/stop')
def stop_brew():
    machine.stop()
    controller.set_temperature(20.0)
    return redirect('/')


@app.route('/status/temperature', methods=['GET'])
def temperature():
    return jsonify(temperature=controller.get_temperature())
