from flask import request, render_template
from brew import app
from brew.models import recipes


@app.route('/')
def index():
    return render_template('index.html', recipes=recipes)


@app.route('/recipe/create', methods=['GET', 'POST'])
def create_recipe():
    if request.method == 'POST':
        print(request.get_json())
    return render_template('create.html')


@app.route('/prepare/<recipe_id>')
def prepare(recipe_id):
    return render_template('prepare.html', recipe=recipes[0])
