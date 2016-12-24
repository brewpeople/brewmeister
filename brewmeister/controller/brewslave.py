import os
import re
import time
import struct
import serial
import threading
import crcmod


COMMAND_GET = struct.pack('B', 0xf0)
COMMAND_SET = struct.pack('B', 0xf1)

DS18B20 = struct.pack('B', 0xf1)
HEATER = struct.pack('B', 0xf2)
STIRRER = struct.pack('B', 0xf3)


# Contrary to crcmod's definition, brewslave expects a bit-reversed CRC
crc8 = crcmod.mkCrcFun(0x131, 0, False, 0)


class Brewslave(object):

    def __init__(self, app):
        device = None

        for x in os.listdir('/dev'):
            if re.match(r"tty(ACM.|USB.|\.usbserial.*|\.usbmodem.*)", x):
                device = os.path.join('/dev', x)
                break

        self.app = app
        self.conn = serial.Serial(device, timeout=2, baudrate=115200)
        self._lock = threading.Lock()
        self._heating = False
        self._stirring = False
        self._target = self._read_temperature()

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
                self.conn.read(1)
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

    @property
    def temperature(self):
        return self._read_temperature()

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, temperature):
        self._target = temperature
        is_set = False

        while not is_set:
            try:
                self._write_float(DS18B20, temperature)
                is_set = True
            except IOError:
                # TODO: this is unbounded!
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
