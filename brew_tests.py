import flask
import struct
import unittest
from brew.io import ArduinoController


class TestConnection(object):
    def __init__(self, data):
        self.data = data
        self.do_reply = False

    def write(self, data):
        self.data = struct.unpack('B', data)[0]
        self.do_reply = True

    def read(self, n_bytes):
        # Someone just wrote
        if self.do_reply:
            self.do_reply = False
            return struct.pack('B', 0)

        return self.data


class ArduinoInterfaceTest(unittest.TestCase):

    def setUp(self):
        app = flask.Flask(__name__)
        app.config.from_object('brew.settings')
        app.config['BREW_CONTROLLER_TYPE'] = 'arduino'

        self.connection = TestConnection(0)
        self.controller = ArduinoController(app, self.connection)

    def test_set_temperature(self):
        self.controller.set_temperature(20.5)
        self.assertEqual(self.connection.data, 0)

        temperature = self.controller.get_temperature()
        self.assertEqual(self.connection.data >> 6, 1)


if __name__ == '__main__':
    unittest.main()
