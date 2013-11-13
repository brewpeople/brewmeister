from flask import request, render_template
from bson.objectid import ObjectId
from brew import app, mongo


@app.route('/')
def index():
    recipes = mongo.db.recipes.find()
    return render_template('index.html', recipes=recipes)


@app.route('/recipes', methods=['GET', 'POST'])
def recipes():
    if request.method == 'POST':
        mongo.db.recipes.insert(request.get_json())

    return render_template('create.html')


@app.route('/prepare/<recipe_id>', methods=['GET'])
def prepare(recipe_id):
    recipe = mongo.db.recipes.find_one(ObjectId(recipe_id))
    return render_template('prepare.html', recipe=recipe)


@app.route('/brew/<recipe_id>', methods=['POST'])
def brew(recipe_id):
    return "Create new brew with {} L".format(request.form['amount'])
