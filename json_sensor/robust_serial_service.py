import asyncio
import logging
import mode
import janus
from mode import Service, OneForOneSupervisor, Signal, SignalT

import serial
from serial.threaded import LineReader, ReaderThread
import threading

import enum



class SerialData(dict):
    ...
class EventConnectionMade:
    ...
class EventConnectionLost:
    ...


class JanusLineReader(LineReader):
    @property
    def parent(self):
        return self._parent
    
    @parent.setter
    def parent(self, value):
        self._parent = value

    def connection_made(self, transport):
        # super(JanusLineReader, self).connection_made(transport)
        super().connection_made(transport)
        # self.parent.log.debug(f'port opened ({self.parent.device}, thread {threading.get_ident()})')
        self.parent.read_queue_sync.put(EventConnectionMade())

        # self.write_line('hello world')

    def handle_line(self, data):
        # self.parent.log.debug(f'({self.parent.device}): line received: {repr(data)} (thread {threading.get_ident()})')
        data_wrap = SerialData({'data_raw': data})
        self.parent.read_queue_sync.put(data_wrap)

    def connection_lost(self, exc):
        if exc:
            self.parent.log.exception(exc)
            # await self.parent.crash(exc)
        self.parent.read_queue_sync.put(EventConnectionLost())
        # self.parent.log.debug('port closed')



class RobustSerialService(Service):  
    on_data: SignalT = Signal()
    on_connection_made: SignalT = Signal()
    on_connection_lost: SignalT = Signal()

    def __init__(self, device, baudrate=115200, timeout=1, protocol_factory=JanusLineReader, **kwargs) -> None:
        super().__init__(**kwargs)

        self._device = device
        self.baudrate = baudrate
        self.timeout = timeout

        self.on_data = self.on_data.with_default_sender(self)
        self.on_connection_made = self.on_connection_made.with_default_sender(self)
        self.on_connection_lost = self.on_connection_lost.with_default_sender(self)

        self.read_queue = janus.Queue(loop=self.loop) 
        self.set_protocol_factory(protocol_factory)

    def set_protocol_factory(self, protocol_factory):
        self._protocol_factory = protocol_factory

    def make_bound_parser(self, *arg, **kwds):
        protocol = self._protocol_factory(*arg, **kwds)
        protocol.parent = self
        return protocol

    async def on_start(self):
        # self.log.info(f'RobustSerialService: {self.device} in thread {threading.get_ident()}')
        self.log.info(f'Starting on {self.device}')

        ser = serial.serial_for_url(self.device, baudrate=self.baudrate, timeout=self.timeout)       
        self.reader_thread = self.add_context(ReaderThread(ser, self.make_bound_parser))

    async def on_stop(self) -> None:
        self.log.info('RobustSerialService on_stop')
        

    async def transform_data(self, data_raw):
        ''' override this fuction in a subclass to refine data analysis '''
        return data_raw

    @property
    def read_queue_sync(self):
        return self.read_queue.sync_q

    @Service.task
    async def _pump_data(self) -> None:
        self.log.debug('pump_data TASK STARTING')
        while not self.should_stop:
            data = await self.read_queue.async_q.get()
            if type(data) == SerialData:
                self.log.debug(f'async thread {threading.get_ident()}: SerialData: {data["data_raw"]}')                               
                trafo_data = await self.transform_data(data["data_raw"])
                await self.on_data.send(data = trafo_data)
            elif type(data) == EventConnectionMade:
                self.log.debug(f'async thread {threading.get_ident()}: EventConnectionMade')
                await self.on_connection_made.send()
            elif type(data) == EventConnectionLost:
                self.log.debug(f'async thread {threading.get_ident()}: EventConnectionLost')
                await self.on_connection_lost.send()
                await self.crash(RuntimeError('Connection lost!'))

    @property
    def device(self):
        return self._device



def test_robust_serial():
    from mode import Worker

    supervisor = OneForOneSupervisor()
    connection = RobustSerialService(\
            device = '/dev/ttyACM0',
            baudrate = 9600,
            timeout = 10,
            protocol_factory = JanusLineReader
        )

    supervisor.add(connection)

    Worker(supervisor, loglevel="debug").execute_from_commandline()

if __name__ == '__main__':
    test_robust_serial()
  