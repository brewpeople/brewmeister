import time
import jsonschema
from flask import request, jsonify, make_response, abort
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
        return "", 201

    return "", 200


@app.route('/api/brews', methods=['GET'])
def get_brews():
    brews = [str(each['_id']) for each in mongo.db.brews.find()]
    return jsonify(brews=brews)


@app.route('/api/brews/<brew_id>', methods=['GET'])
def get_brew_details(brew_id):
    # Lame attempt to avoid serialization of the _id
    brew = mongo.db.brews.find_one(ObjectId(brew_id))

    if not brew:
        abort(401)

    return jsonify({k: v for k, v in brew.items() if k != '_id'})


@app.route('/api/brews/<brew_id>/note', methods=['PUT'])
def update_brew(brew_id):
    note = request.get_json()
    brew = mongo.db.brews.find_one(ObjectId(brew_id))

    if not 'note' in note:
        abort(400)

    if not brew:
        abort(401)

    brew['note'] = note['note']
    d = {'_id': ObjectId(brew['_id'])}
    mongo.db.brews.update(d, brew, True)
    return "", 201


@app.route('/api/brews/<brew_id>/temperature', methods=['GET'])
def brew_temperature(brew_id):
    brew = mongo.db.brews.find_one(ObjectId(brew_id))

    if not brew:
        abort(401)

    temperatures = [(int(t * 1000), temp) for (t, temp) in brew['temperatures']]
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
    return "", 201


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(timestamp=int(time.time() * 1000),
                   state=machine.fsm.current,
                   step=machine.current_step,
                   connected=controller.connected,
                   heating=controller.heating,
                   stirring=controller.stirring,
                   slope=controller.slope,
                   temperature=controller.temperature)


@app.route('/api/status/<device>', methods=['GET'])
def device_status(device):
    if not hasattr(controller, device):
        abort(401)

    return jsonify(status=getattr(controller, device))


@app.route('/api/start/<device>', methods=['PUT'])
def start(device):
    if not hasattr(controller, device):
        abort(401)

    setattr(controller, device, True)
    return ""


@app.route('/api/stop/<device>', methods=['PUT'])
def stop(device):
    if not hasattr(controller, device):
        abort(401)

    setattr(controller, device, False)
    return ""


@app.route('/api/reconnect', methods=['PUT'])
def reconnect():
    controller.reconnect()
    return jsonify(connected=controller.connected)
