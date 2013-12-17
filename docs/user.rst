Installation
============

Prepare a virtualenv_ and install all requirements::

    $ pip install --upgrade -r requirements.txt

Setup a MongoDB instance, e.g. ::

    $ sudo apt-get install mongodb-server

For testing purposes you can pre-populate the database with::

    $ make init

Generate translation data base and run the debug server with::

    $ make

By default, a dummy controller is running with which you can brew a virtual
beer.


.. _virtualenv: http://www.virtualenv.org/en/latest/


Customization
-------------

You can edit ``brew/settings.py`` and change the following configuration options:

==================================  ===========================================
``BREW_CONTROLLER_TYPE``            Can be either ``dummy`` or ``arduino``.
``BREW_CONTROLLER_ARDUINO_DEVICE``  Device filename of the serial connection to
                                    the Arduino device. It is is
                                    ``/dev/ttyUSB0`` by default.
``BREW_CONTROLLER_DUMMY_SLOPE``     Temperature increase in degrees per minute
                                    of the dummy controller.
==================================  ===========================================
