import time 
import threading
import logging
import asyncio
import janus
import json

import serial

from json_sensor.robust_serial_service import *


class JsonSensor(RobustSerialService):

    async def on_start(self):
        await super().on_start()
        self.has_valid_data = False
        self.skipped_first_line = False

    @Service.timer(3.0)
    async def check_validity(self):
        if not self.has_valid_data:
            await self.crash(RuntimeError(f'This sensor ({self.device})does not deliver valid data in time!'))
        # reset
        self.has_valid_data = False

    async def transform_data(self, data_raw):
        ''' override this fuction in a subclass to refine data analysis '''
        super_data = await super().transform_data(data_raw)

        if self.skipped_first_line:
            try:
                parsed_data = json.loads(super_data)                
                self.last_data = parsed_data
                self.has_valid_data = True

                self.last_data['json_receive_time'] = time.time()

            except BaseException as e:
                self.logger.debug('Data from sensor creates error: ' + str(repr(e)))
                parsed_data = dict()
                parsed_data['error'] = repr(e)
        else:
            self.skipped_first_line = True
            self.log.debug('Skipping first (possibly) incomplete line!')
            parsed_data = None

        return parsed_data






# class JsonSensorFactors(object):

#     def __init__(self, config_file = None):
#         self.config = {}

#         if config_file is not None:
#             self.set_config_file(config_file)

#     def load_config_file(self, config_file):
#         self.config_file = config_file

#         with open(self.config_file) as f:
#             self.config = json.load(f)

#     def save_config_file(self, config_file = None):
#         if config_file is not None:
#             self.config_file = config_file

#         with open(self.config_file, 'w') as f:
#             json.dump(f, self.config)

#     def add_sensor_config(self, dev_path, logic_path, **kwds):
#         self.config[logic_path] = dict(\
#                 dev_path=dev_path,
#                 **kwds
#             )



#     async def start(self):
#         self.run_task = asyncio.ensure_future(self.run())

#     async def run(self):
#         while self.running.is_set():
#             ser = serial.serial_for_url(self.dev_path, baudrate=self.baudrate, timeout=self.timeout)
#             with ReaderThread(ser, self.make_bound_parser) as protocol:
#                 # just hang out. rest happens in the thread/queue
#                 await asyncio.sleep(0.5)





# serial.tools.list_ports
# https://pythonhosted.org/pyserial/tools.html#module-serial.tools.list_ports



def test_json_sensor():
    from mode import Worker

    supervisor = OneForOneSupervisor()
    connection = JsonSensor(\
            device = '/dev/ttyACM0',
            baudrate = 9600,
            timeout = 10
        )

    class DataReader(Service):
        @Service.timer(5.0)
        async def interfere(self):
            await connection.crash(RuntimeError('Something went wrong... Hehehe...'))
            self.log.info('poll')

        async def handle_data(self, sender, data={}, **kwds):
            # self.log.info('Got data: ' + repr(data))
            self.log.info('Got data: sender:' +  repr(sender) + ' data: ' + repr(data))

            
    data_reader = DataReader()

    connection.on_data.connect(data_reader.handle_data)

    supervisor.add(connection)
    supervisor.add(data_reader)

    # Worker(supervisor, loglevel="debug").execute_from_commandline()
    Worker(supervisor, loglevel="info").execute_from_commandline()

if __name__ == '__main__':
    test_json_sensor()
  