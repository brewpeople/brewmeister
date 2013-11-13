from flask import request, jsonify
from brew import app
from brew.models import recipes


@app.route('/api/recipes', methods=['POST', 'GET'])
def get_recipes():
    if request.method == 'POST':
        print(request.get_json())
        return 'OK'
    else:
        return jsonify(recipes=recipes)


@app.route('/api/brews/<brew_id>/start', methods=['PUT'])
def start_brew(brew_id):
    return 'Start brewing'
