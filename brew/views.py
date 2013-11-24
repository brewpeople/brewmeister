import json
import jsonschema
import uuid
import time
import datetime
import cStringIO
import math
from flask import request, render_template, jsonify, redirect, url_for, make_response
from flask.ext.babel import format_datetime
from bson.json_util import dumps
from bson.objectid import ObjectId
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPDF
from brew import app, babel, controller, machine, mongo, monitor
from brew.monitor import Monitor
from schema import loads as load_schema


current_brew = None
monitor = Monitor()


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'de'])


@app.template_filter('datetime')
def datetime_filter(value):
    fmt = "EE, dd.MM.y"
    return format_datetime(value, fmt)


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
                mash=mash, date=datetime.datetime.now(),
                amount=amount, brewers=brewers, temperatures=[])

    mongo.db.brews.insert(brew)
    return brew


@app.route('/')
def index():
    recipes = mongo.db.recipes.find()
    brews = mongo.db.brews.find()
    return render_template('index.html', recipes=recipes, brews=brews,
                           current_brew=current_brew)


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


@app.route('/label/brew/<brew_id>', methods=['GET'])
def brew_label_view(brew_id):
    page_width, page_height = A4
    page_margin = 10.0
    qr_width, qr_height = 60.0, 60.0

    qr_margin = 5.0     # this is a desired margin, not the actual one
    num_rows = int(math.floor((page_height - 2 * page_margin) / (qr_height + qr_margin)))
    num_cols = int(math.floor((page_width - 2 * page_margin) / (qr_width + qr_margin)))

    qr_vertical_margin = ((page_height - 2 * page_margin) - num_rows * qr_height) / num_rows
    qr_horizontal_margin = ((page_width - 2 * page_margin) - num_cols * qr_width) / num_cols

    qr = QrCodeWidget('http://127.0.0.1/view/{}'.format(brew_id))
    output = cStringIO.StringIO()
    p = canvas.Canvas(output, pagesize=A4)
    b = qr.getBounds()
    w, h = b[2]-b[0], b[3]-b[1]

    d = Drawing(qr_width, qr_height,
                transform=[qr_width / w, 0, 0, qr_height / h, 0, 0])
    d.add(qr)

    for i in xrange(num_cols):
        x = page_margin + i * (qr_horizontal_margin + qr_width)

        for j in xrange(num_rows):
            y = page_margin + j * (qr_vertical_margin + qr_height)
            renderPDF.draw(d, p, x, y)

    p.showPage()
    p.save()

    pdf_output = output.getvalue()
    output.close()

    response = make_response(pdf_output)
    response.headers['Content-Disposition'] = 'attachment; filename=qr.pdf'
    response.mimetype = 'application/pdf'
    return response


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
    controller.set_temperature(20.0)
    current_brew = None
    return redirect('/')
