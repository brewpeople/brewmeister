import json
import jsonschema
from pkg_resources import resource_string
from flask import request, render_template, jsonify, redirect
from bson.objectid import ObjectId
from brew import app, mongo, controller, machine


def create_brew(recipe_id, brewers):
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))
    mash = []

    for step in recipe['mash']:
        mash.append(dict(name=step['name'],
                         time=step['time'],
                         temperature=step['temperature'],
                         state='waiting'))
        mash[0]['state'] = 'pending'

    return dict(recipe_id=recipe_id, mash=mash, brewers=brewers)


def prepare_machine(mash):
    for step in mash:
        machine.append_heat_change(step['temperature'])
        machine.append_rest(step['time'])


@app.route('/')
def index():
    recipes = mongo.db.recipes.find()
    return render_template('index.html', recipes=recipes, machine=machine)


@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    schema = resource_string(__name__, 'data/recipe.schema.json').decode('utf-8')

    if request.method == 'POST':
        recipe_json = request.get_json()
        schema_dict = json.loads(schema)
        jsonschema.validate(schema_dict, recipe_json)
        mongo.db.recipes.insert(recipe_json)

    return render_template('create.html', schema=schema)


@app.route('/brews/prepare/<recipe_id>', methods=['GET'])
def prepare(recipe_id):
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))
    return render_template('prepare.html', recipe=recipe)


@app.route('/brews', methods=['GET', 'POST'])
def brew():
    if request.method == 'POST':
        recipe_id = request.form['recipe_id']
        brew = create_brew(recipe_id, [u"Michael Jackson"])
        prepare_machine(brew['mash'])
        machine.start()

    return render_template('brew.html', brew=brew, machine=machine)


@app.route('/brews/stop', methods=['POST'])
def stop_brew():
    machine.stop()
    controller.set_temperature(20.0)
    return "okay"
    # return redirect('/')


@app.route('/status/temperature', methods=['GET'])
def temperature():
    return jsonify(temperature=controller.get_temperature())
