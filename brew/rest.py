import json
import time
import jsonschema
from pkg_resources import resource_string
from flask import request, jsonify
from brew import app, controller, machine, mongo


@app.route('/api/recipe', methods=['POST'])
def create_recipe():
    schema = resource_string(__name__, 'data/recipe.schema.json').decode('utf-8')
    recipe_json = request.get_json()
    schema_dict = json.loads(schema)
    jsonschema.validate(schema_dict, recipe_json)
    mongo.db.recipes.insert(recipe_json)

    for malt in recipe_json['malts']:
        d = {'name': malt['name']}
        mongo.db.malts.update(d, d, True)

    return jsonify(success=True)


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(timestamp=int(time.time() * 1000),
                   step=machine.current_step,
                   temperature=controller.get_temperature())
