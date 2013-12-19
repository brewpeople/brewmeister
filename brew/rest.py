import time
import jsonschema
from flask import request, jsonify, make_response
from bson.objectid import ObjectId
from brew import app, controller, machine, mongo
from schema import loadd as load_schema
from qr import make_pdf


@app.route('/api/recipe', methods=['POST'])
@app.route('/api/recipe/<recipe_id>', methods=['PUT'])
def recipe(recipe_id=None):
    recipe_json = request.get_json()
    schema_dict = load_schema('data/recipe.schema.json')
    jsonschema.validate(schema_dict, recipe_json)

    for malt in recipe_json['malts']:
        d = {'name': malt['name']}
        mongo.db.malts.update(d, d, True)

    if request.method == 'POST':
        mongo.db.recipes.insert(recipe_json)
    elif request.method == 'PUT':
        d = {'_id': ObjectId(recipe_id)}
        mongo.db.recipes.update(d, recipe_json, False)

    return jsonify(success=True)


@app.route('/api/brews/<brew_id>/temperature', methods=['GET'])
def brew_temperature(brew_id):
    brew = mongo.db.brews.find_one(ObjectId(brew_id))
    temperatures = [(int(t * 1000), temp)
                    for (t, temp) in brew['temperatures']]
    return jsonify(temperatures=temperatures)


@app.route('/api/brews/<brew_id>/label', methods=['GET'])
def get_brew_label(brew_id):
    output = make_pdf('http://127.0.0.1/view/{}'.format(brew_id))
    response = make_response(output)
    response.headers['Content-Disposition'] = 'attachment; filename=qr.pdf'
    response.mimetype = 'application/pdf'
    return response


@app.route('/api/brews/<brew_id>/label/prepare', methods=['GET'])
def prepare_brew_label(brew_id):
    output = make_pdf('http://127.0.0.1/view/{}'.format(brew_id))
    return jsonify(success=True)


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(timestamp=int(time.time() * 1000),
                   step=machine.current_step,
                   temperature=controller.get_temperature())


@app.route('/api/status/<device>', methods=['GET'])
def device_status(device):
    if hasattr(controller, device):
        return jsonify(status=getattr(controller, device), success=True)

    return jsonify(success=False)


@app.route('/api/start/<device>', methods=['PUT'])
def start(device):
    if hasattr(controller, device):
        setattr(controller, device, True)

    return jsonify(success=True)


@app.route('/api/stop/<device>', methods=['PUT'])
def stop(device):
    if hasattr(controller, device):
        setattr(controller, device, False)

    return jsonify(success=True)
