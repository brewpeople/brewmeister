import json
import jsonschema
import uuid
import time
import datetime
from pkg_resources import resource_string
from flask import request, render_template, jsonify, redirect, url_for
from flask.ext.babel import format_datetime
from bson.objectid import ObjectId
from brew import app, babel, controller, machine, mongo


current_brew = None

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)

        return json.JSONEncoder.default(self, o)


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'de'])


@app.template_filter('datetime')
def datetime_filter(value):
    fmt = "EE, dd.MM.y"
    return format_datetime(value, fmt)


def create_brew(recipe_id, brewers):
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))
    mash = []

    for step in recipe['mash']:
        mash.append(dict(id=uuid.uuid4(),
                         name=step['name'],
                         time=step['time'],
                         temperature=step['temperature'],
                         state=''))

    brew = dict(recipe=recipe['name'], recipe_id=recipe_id,
                mash=mash, date=datetime.datetime.now(),
                brewers=brewers)

    mongo.db.brews.insert(brew)
    return brew


def get_current_brew():
    return mongo.db.brews.find_one({"current": True})


@app.route('/')
def index():
    recipes = mongo.db.recipes.find()
    brews = mongo.db.brews.find()
    return render_template('index.html', recipes=recipes, machine=machine,
                           brews=brews)


@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    schema = resource_string(__name__, 'data/recipe.schema.json').decode('utf-8')

    if request.method == 'POST':
        recipe_json = request.get_json()
        schema_dict = json.loads(schema)
        jsonschema.validate(schema_dict, recipe_json)
        mongo.db.recipes.insert(recipe_json)
        return redirect(url_for('index'))

    return render_template('create.html', schema=schema)


@app.route('/brews', methods=['GET', 'POST'])
def brew():
    if request.method == 'POST':
        global current_brew

        recipe_id = request.form['recipe_id']
        current_brew = create_brew(recipe_id, [u"Michael Jackson"])
        machine.reset()

        for step in current_brew['mash']:
            machine.append_step(step)

        machine.start()

    return render_template('brew.html', brew=current_brew, machine=machine)


@app.route('/brews/<brew_id>', methods=['GET'])
def get_brew(brew_id):
    brew = mongo.db.brews.find_one(ObjectId(brew_id))
    return render_template('details.html', brew=brew)


@app.route('/stop', methods=['POST'])
def stop_brew():
    global current_brew

    machine.stop()
    controller.set_temperature(20.0)
    current_brew = None
    return redirect('/')


@app.route('/brews/delete/<brew_id>', methods=['GET'])
def delete_brew(brew_id):
    mongo.db.brews.remove(ObjectId(brew_id))
    return redirect(url_for('index'))


@app.route('/brews/prepare/<recipe_id>', methods=['GET'])
def prepare(recipe_id):
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))
    return render_template('prepare.html', recipe=recipe)


@app.route('/status', methods=['GET'])
def status():
    return jsonify(timestamp=int(time.time() * 1000),
                   step=machine.current_step,
                   temperature=controller.get_temperature())
