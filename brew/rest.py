import json
import time
import jsonschema
from flask import request, jsonify
from bson.objectid import ObjectId
from brew import app, controller, machine, mongo
from schema import loadd as load_schema



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


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(timestamp=int(time.time() * 1000),
                   step=machine.current_step,
                   temperature=controller.get_temperature())
