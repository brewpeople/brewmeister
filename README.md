## Brewmeister · Homebrewing 2.0

Brewmeister is a server application to organize and control [beer brewing
processes](http://en.wikipedia.org/wiki/Brewing). It provides an HTML interface
for human brewers and a REST-API for machine consumption.


### Features

* Based on Flask + MongoDB
* Simple REST-API
* Full internationalization and localization for German
* Client- and server-side validation via schemas
* Temperature control based on a state machine
* Absolutely _no_ security measures


### Setup

Prepare a [virtualenv](http://www.virtualenv.org/en/latest/) and install all
requirements:

    $ pip install --upgrade -r requirements.txt

Setup a MongoDB instance, e.g.

    $ sudo apt-get install mongodb-server

For testing purposes you can pre-populate the database with

    $ python manage.py populatedb

Generate translation data base and run the debug server with

    $ python manage.py compilepo
    $ python manage.py runserver

By default, a dummy controller is running with which you can brew a virtual
beer.


### Customization

The following config options are available:

* `CONTROLLER_TYPE`: one of `['dummy', 'arduino']`
* `CONTROLLER_ARDUINO_DEVICE`: device filename (`/dev/ttyUSB0` per default)
* `CONTROLLER_DUMMY_SLOPE`: temperature increase in degrees per minute 


### Screenshot

![screenshot](http://i.imgur.com/TGDSKAO.png)
