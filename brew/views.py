import json
import jsonschema
import uuid
from pkg_resources import resource_string
from flask import request, render_template, jsonify, redirect
from bson.objectid import ObjectId
from brew import app, babel, controller, machine, mongo


current_brew = None

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'de'])


def create_brew(recipe_id, brewers):
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))
    mash = []

    for step in recipe['mash']:
        mash.append(dict(id=uuid.uuid4(),
                         name=step['name'],
                         time=step['time'],
                         temperature=step['temperature'],
                         state=''))

    brew = dict(recipe_id=recipe_id, mash=mash, brewers=brewers)
    mongo.db.brews.insert(brew)
    return brew


def get_current_brew():
    return mongo.db.brews.find_one({"current": True})


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
        global current_brew

        recipe_id = request.form['recipe_id']
        current_brew = create_brew(recipe_id, [u"Michael Jackson"])

        for step in current_brew['mash']:
            machine.append_step(step)

        machine.start()

    return render_template('brew.html', brew=current_brew, machine=machine)


@app.route('/brews/stop', methods=['POST'])
def stop_brew():
    machine.stop()
    controller.set_temperature(20.0)


@app.route('/status', methods=['GET'])
def temperature():
    return jsonify(step=machine.current_step,
                   temperature=controller.get_temperature())
