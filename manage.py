import json
import subprocess
from flask.ext.script import Manager
from brew import app, mongo


manager = Manager(app)


@manager.command
def populatedb():
    with open('recipes.json', 'r') as f:
        mongo.db.recipes.insert(json.load(f))


@manager.command
def updatepot():
    cmd = 'pybabel extract -F babel.cfg -o messages.pot .'
    subprocess.check_call(cmd.split())

    cmd = 'pybabel update -i messages.pot -d brew/translations'
    subprocess.check_call(cmd.split())


@manager.command
def createpo(lang):
    cmd = 'pybabel init -i messages.pot -d brew/translations -l' + lang
    subprocess.check_call(cmd.split())


@manager.command
def compilepo():
    cmd = 'pybabel compile -f -d brew/translations'
    subprocess.check_call(cmd.split())


if __name__ == '__main__':
    manager.run()
