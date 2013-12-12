#! python

import json
from flask.ext.script import Manager
from brew import app, mongo


manager = Manager(app)


@manager.command
def populatedb():
    with open('recipes.json', 'r') as f:
        mongo.db.recipes.insert(json.load(f))


if __name__ == '__main__':
    manager.run()
