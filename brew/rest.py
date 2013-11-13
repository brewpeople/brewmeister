from flask import request, jsonify
from brew import app, mongo


@app.route('/api/brews/<brew_id>/start', methods=['PUT'])
def start_brew(brew_id):
    return 'Start brewing'
