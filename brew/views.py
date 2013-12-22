import uuid
import datetime
from docutils.core import publish_parts
from flask import request, render_template, redirect, url_for
from flask.ext.babel import format_datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
from brew import app, babel, controller, machine, mongo
from brew.monitor import Monitor
from schema import loads as load_schema


current_brew = None
monitor = Monitor()
LANG_CODES = ['en', 'de', 'cs']


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANG_CODES)


@app.template_filter('datetime')
def datetime_filter(value):
    fmt = "EE, dd.MM.y"
    return format_datetime(value, fmt)


@app.template_filter('rst2html')
def rst_filter(value):
    parts = publish_parts(value, writer_name='html')
    return parts['fragment']


def create_brew(recipe_id, amount, brewers):
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))
    mash = []

    for step in recipe['mash']:
        mash.append(dict(id=uuid.uuid4(),
                         name=step['name'],
                         time=step['time'],
                         temperature=step['temperature'],
                         state=''))

    brew = dict(recipe=recipe['name'], recipe_id=recipe_id,
                mash=mash, date=datetime.datetime.now(), note="",
                amount=amount, brewers=brewers, temperatures=[])

    mongo.db.brews.insert(brew)
    return brew


@app.route('/')
def index():
    recipes = mongo.db.recipes.find()
    brews = mongo.db.brews.find()
    return render_template('index.html',
                           recipes=recipes, brews=brews,
                           controller=controller, current_brew=current_brew)


@app.route('/create/recipe', methods=['GET'])
def create_recipe_view():
    schema = load_schema('data/recipe.schema.json')
    return render_template('create.html', schema=schema)


@app.route('/edit/recipe/<recipe_id>', methods=['GET'])
def edit_recipe_view(recipe_id):
    recipe = dumps(mongo.db.recipes.find_one(ObjectId(recipe_id)))
    schema = load_schema('data/recipe.schema.json')
    return render_template('edit.html', schema=schema, recipe=recipe,
                           recipe_id=recipe_id)


@app.route('/delete/recipe/<recipe_id>', methods=['GET'])
def delete_recipe(recipe_id):
    mongo.db.recipes.remove(ObjectId(recipe_id))
    return redirect(url_for('index'))


@app.route('/prepare/brew/<recipe_id>', methods=['GET'])
def prepare_brew_view(recipe_id):
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))
    return render_template('prepare.html', recipe=recipe)


@app.route('/brews', methods=['GET', 'POST'])
def brews_view():
    if request.method == 'POST':
        global current_brew

        recipe_id = request.form['recipe_id']
        brewers = request.form['brewers'].split(',')
        amount = float(request.form['amount'])
        current_brew = create_brew(recipe_id, amount, brewers)

        monitor.temperature(current_brew['_id'])
        machine.reset()

        for step in current_brew['mash']:
            machine.append_step(step)

        machine.start()

    return render_template('brew.html', brew=current_brew, machine=machine)


@app.route('/view/brew/<brew_id>', methods=['GET'])
def get_brew(brew_id):
    brew = mongo.db.brews.find_one(ObjectId(brew_id))
    return render_template('details.html', brew=brew)


@app.route('/delete/brew/<brew_id>', methods=['GET'])
def delete_brew(brew_id):
    mongo.db.brews.remove(ObjectId(brew_id))
    return redirect(url_for('index'))


@app.route('/stop', methods=['GET', 'POST'])
def stop_brew():
    global current_brew

    monitor.stop()
    machine.stop()
    controller.set_reference_temperature(20.0)
    current_brew = None
    return redirect('/')
