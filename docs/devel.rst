===========
Development
===========


Contributing
============

Translations
------------

The easiest way to add or improve translations is to go to the Transifex
`project page <https://www.transifex.com/projects/p/brewmeister>`_ and request
a new language or start digging on the existing ones. This is the preferred way
for translators, as the messages source file is uploaded when necessary.

You can also add and translate manually. First create a new language with ``make
createpo``, enter the targetted language code and edit the translation file in
``brew/translations/<lang>/LC_MESSAGES/messages.po``. Once finished, you can add
and commit this file and issue a pull request on GitHub.


Arduino Brew Control Protocol
=============================

The Arduino Brew Control Protocol (short ABCP) is a *simple*, *compact*,
*stateless* and *command-based* wire protocol for communicating with a
Brewmeister-compatible Arduino.

The following specification assumes, the *host* to be the machine that
communicates with the Arduino via a serial line interface.


Protocol sequence
-----------------

Communication is *always* initiated by the host using a simple call-response
sequence:

1. Host sends command packet specifying either to *read* or to *write* data.
2. Host sends device packet specifying which device is addressed.
3. In case of a *write* command, the host sends the data.
4. The Arduino answers with a status code and depending on the command, optional
   data.


Command packet
--------------

The command packet is sent by the host and consists of one byte:

* ``0xf0`` get data from device
* ``0xf1`` set data on device

The device byte can be

======  ==============  =========
Code    Instrument      Data type
======  ==============  =========
0xf1    Temperature     float
0xf2    Heat            byte
0xf3    Stir            byte
======  ==============  =========


RESTful HTTP API
================

.. http:post:: /api/recipe/(int:recipe_id)

    Recipe data of (`recipe_id`).

.. http:get:: /api/brews/(int:brew_id)/temperature

    Archived temperature data for (`brew_id`).

.. http:get:: /api/status

    Status of the current brew.
