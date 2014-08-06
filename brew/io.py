import time
import random
import serial
import struct
import threading
import crcmod


COMMAND_GET = struct.pack('B', 0xf0)
COMMAND_SET = struct.pack('B', 0xf1)

DS18B20 = struct.pack('B', 0xf1)
HEATER = struct.pack('B', 0xf2)
STIRRER = struct.pack('B', 0xf3)


# Contrary to crcmod's definition, brewslave expects a bit-reversed CRC
crc8 = crcmod.mkCrcFun(0x131, 0, False, 0)


def TemperatureController(app):
    controller_type = app.config.get('BREW_CONTROLLER_TYPE', 'dummy')

    if controller_type == 'arduino':
        return ArduinoController(app)
    elif controller_type == 'dummy':
        return DummyController(app)

    raise ValueError("Unknown controller type")


class Controller(object):
    def __init__(self, app, ttl=2):
        self.app = app
        self._last_times = (0, 0)
        self._last_temperatures = (0, 0)
        self._ttl = ttl

    def reconnect(self):
        raise NotImplementedError

    @property
    def connected(self):
        raise NotImplementedError

    @property
    def slope(self):
        """Return temperature slope in degree Celsius per Minute"""
        time_first, time_second = self._last_times
        temp_first, temp_second = self._last_temperatures
        elapsed = time_second - time_first
        delta = temp_second - temp_first

        if elapsed > 0:
            return delta / elapsed * 60.0

        return 0

    @property
    def temperature(self):
        """Temperature in degree celsius"""
        current_time = time.time()

        if current_time < self._last_times[1] + self._ttl:
            return self._last_temperatures[1]

        try:
            temperature = self._read_temperature()

            if temperature:
                self._last_temperatures = (self._last_temperatures[1], temperature)
                self._last_times = (self._last_times[1], current_time)
        except IOError as error:
            self.app.log.warning(str(error))

        return self._last_temperatures[1]

    def _read_temperature(self):
        raise NotImplementedError


class ArduinoController(Controller):

    def __init__(self, app):
        super(ArduinoController, self).__init__(app)
        import os
        import re
        for x in os.listdir('/dev'):
            if re.match(r"tty(ACM.|USB.|\.usbserial.*|\.usbmodem.*)", x):
                device_address = '/dev/'+x
                break
            else:
                device_address = 'none'
        self.filename = app.config.get('BREW_CONTROLLER_ARDUINO_DEVICE', device_address)
        self.app = app
        self.status = None
        self._lock = threading.Lock()
        self._heating = False
        self._stirring = False
        self.reconnect()

    @property
    def connected(self):
        return self.conn != None

    def reconnect(self):
        try:
            self.conn = serial.Serial(self.filename, timeout=2, baudrate=115200)
            self.status = ""
        except OSError as exception:
            self.conn = None
            self.status = str(exception)

    def _send_packet(self, command, device, payload_fmt=None, *payload):
        if not payload:
            packet = struct.pack('ssBBBB', command, device, 0, 0, 0, 0)
        else:
            packet = struct.pack('ss{}'.format(payload_fmt), command, device, *payload)

        checksum = struct.pack('B', crc8(packet))
        self.conn.write(packet)
        self.conn.write(checksum)

    def _write_checked(self, device, payload_fmt, *payload):
        if self.connected:
            try:
                self._lock.acquire()
                self._send_packet(COMMAND_SET, device, payload_fmt, *payload)

                # Read ack byte
                data = self.conn.read(1)
            finally:
                self._lock.release()
        else:
            raise IOError("Not connected")

    def _read_checked(self, device, num_bytes=7):
        if not self.connected:
            raise IOError("Not connected")

        try:
            self._lock.acquire()
            self._send_packet(COMMAND_GET, device)
            data = self.conn.read(num_bytes)

            if not data:
                raise IOError("Received no data")

            if len(data) != num_bytes:
                raise IOError("Received {} != {} bytes".format(len(data), num_bytes))

            checksum = struct.unpack('B', data[6])[0]
            expected = crc8(data[:6])

            if checksum != expected:
                raise IOError("Checksum {} does not match {}".format(checksum, expected))

            return data
        finally:
            self._lock.release()

    def _read_boolean(self, device):
        data = self._read_checked(device)
        received_device, result = struct.unpack('BB', data[0:2])
        return result != 0

    def _read_float(self, device):
        data = self._read_checked(device)
        received_device, status = struct.unpack('BB', data[0:2])
        result = struct.unpack('f', data[2:6])[0]
        return result

    def _write_boolean(self, device, value):
        self._write_checked(device, '?BBB', value, 0, 0, 0)

    def _write_float(self, device, value):
        self._write_checked(device, 'f', value)

    def _read_temperature(self):
        try:
            return self._read_float(DS18B20)
        except serial.SerialException as exception:
            self.app.logger.warning("Serial connection problem: {}".format(str(exception)))
        except IOError as exception:
            self.app.logger.warning("temperature: {}".format(str(exception)))

    def set_reference_temperature(self, temperature):
        is_set = False

        while not is_set:
            try:
                self._write_float(DS18B20, temperature)
                is_set = True
            except IOError as exception:
                time.sleep(0.5)

    @property
    def heating(self):
        try:
            self._heating = self._read_boolean(HEATER)
        except IOError as exception:
            self.app.logger.warning("heating: {}".format(str(exception)))

        return self._heating

    @heating.setter
    def heating(self, value):
        self._write_boolean(HEATER, value)

    @property
    def stirring(self):
        try:
            self._stirring = self._read_boolean(STIRRER)
        except IOError as exception:
            self.app.logger.warning("stirring: {}".format(str(exception)))

        return self._stirring

    @stirring.setter
    def stirring(self, value):
        self._write_boolean(STIRRER, value)


class DummyController(Controller):
    def __init__(self, app, current_temperature=20.0):
        """Create a new dummy controller with a given temperature slope in
        degree celsius per minute and a current temperature in degree
        celsius."""
        super(DummyController, self).__init__(app)

        # Adjust the slope to degree per sec
        self._set_temperature = current_temperature
        self._last_temperature = current_temperature
        self._last_time = time.time()

        self._slope = 5 / 60.
        self.heating = False
        self.stirring = False

    def reconnect(self):
        pass

    @property
    def connected(self):
        return True

    def _read_temperature(self):
        current_time = time.time()
        elapsed = current_time - self._last_time
        self._last_time = current_time

        if abs(self._last_temperature - self._set_temperature) < 0.1:
            return self._last_temperature

        # Okay, this is the worst controller *ever*
        if self._last_temperature > self._set_temperature:
            self._last_temperature -= elapsed * self._slope
        else:
            self._last_temperature += elapsed * self._slope

        self.heating = abs(self._last_temperature - self._set_temperature) > 0.5
        self.stirring = self.heating

        return self._last_temperature

    def set_reference_temperature(self, temperature):
        self._set_temperature = temperature


class Monitor(object):
    def __init__(self, controller, record_func, timeout=5):
        self.thread = None
        self.exit_event = None
        self.timeout = timeout
        self.temperature = controller.temperature
        self.controller = controller
        self.record_func = record_func

    def start(self, brew_id):
        if self.thread:
            raise RuntimeError("Brew still ongoing")

        def run_in_background():
            while True:
                if self.exit_event.wait(self.timeout):
                    break

                self.temperature = self.controller.temperature
                self.record_func(brew_id, self.temperature)


        self.exit_event = threading.Event()
        self.thread = threading.Thread(target=run_in_background)
        self.thread.start()

    def stop(self):
        self.exit_event.set()
        self.thread.join()
        self.thread = None
