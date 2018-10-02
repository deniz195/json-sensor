import sys
import time
import serial
from serial.threaded import LineReader, ReaderThread

class PrintLines(LineReader):
    @property
    def parent(self):
        print('setting parent!')
        return self._parent
    
    @parent.setter
    def parent(self, value):
        self._parent = value

    def connection_made(self, transport):
        super(PrintLines, self).connection_made(transport)
        print(f'port opened ({self.parent.parent_data})')
        # self.write_line('hello world')

    def handle_line(self, data):
        print(f'({self.parent.parent_data}): line received: {repr(data)}')

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)
        print('port closed')


class TestConnection(object):
    dev_path = '/dev/ttyACM0'
    baudrate = 9600
    timeout = 10

    parent_data = 'abcde'

    def make_bound_parser(self, *arg, **kwds):
        protocol = PrintLines(*arg, **kwds)
        protocol.parent = self
        return protocol

    def run_test(self):
        ser = serial.serial_for_url(self.dev_path, baudrate=self.baudrate, timeout=self.timeout)
        with ReaderThread(ser, self.make_bound_parser) as protocol:
            while True:
                time.sleep(1)
                print('run_test loop...')


            # just hang out. rest happens in the thread/queue
            


tc = TestConnection()
tc.run_test()
