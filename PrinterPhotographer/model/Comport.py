import serial
import codecs


class Comport:
    def __init__(self, port, bound_rate, byte_size, command):
        self.connect = None
        self.port = port
        self.bound_rate = bound_rate
        self.byte_size = byte_size
        self.command = command

    def initialize(self):
        try:
            self.connect = serial.Serial(
                port=self.port,
                baudrate=self.bound_rate,
                bytesize=self.byte_size,
                stopbits=serial.STOPBITS_ONE
            )
        except FileNotFoundError as err:
            raise err
        except serial.SerialException as err:
            raise err
        except OSError as err:
            raise err

    def check_command(self):
        serial_str = self.connect.readline()
        serial_str = codecs.decode(serial_str, "UTF-8")
        return self.command in serial_str

    def close_port(self):
        self.connect.close()
