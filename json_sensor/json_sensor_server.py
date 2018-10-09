import asyncio
from mode import Service, OneForOneSupervisor
from json_sensor.robust_serial_service import *
from json_sensor.json_sensor import *
from json_sensor.serial_server import *



__global_json_sensor_server = None

def get_server():
    global __global_json_sensor_server
    return __global_json_sensor_server

def initialize_server(*args, **kwds):
    global __global_json_sensor_server
    __global_json_sensor_server = JsonSensorServer(*args, **kwds)
    return __global_json_sensor_server





class JsonSensorServer(USBSerialServer):
    on_data_update: SignalT = Signal()

    def __init__(self,
                 port_greps = [],
                *args, **kwds):

        super().__init__(port_reader_factory=self.json_sensor_factory,
                         port_greps=port_greps,
                          *args, **kwds)

        self.agg_data = {}
        self.on_data_update = self.on_data_update.with_default_sender(self)
        self.sensor_supervisor = OneForOneSupervisor(max_restarts = 3, over = 30)

        self.subscribers = []


    async def json_sensor_factory(self, port_info):
        # print(f'json_sensor_factory on {port_info.device}')
        connection = JsonSensor(\
                device = port_info.device,
                baudrate = 9600,
                timeout = 10,
            )

        connection.on_data.connect(self.handle_data)
        self.sensor_supervisor.add(connection)
        return connection


    async def handle_data(self, sender, data={}, **kwds):
        # self.log.info('Got data: ' + repr(data))
        if data is not None:
            if 'guid' in data:
                sensor_guid = data['guid']
            else:
                sensor_guid = sender.device

            self.agg_data[sensor_guid] = data       
            self.log.debug(f'Got data: sender guid: {sensor_guid} data: {repr(data)}')

            await self.on_data_update.send(data = data, aggregated_data = self.aggregated_data)
            await self.send_to_subscribers(sensor_guid, data)

    @property
    def aggregated_data(self):
        return self.agg_data

    def create_subscriber_queue(self, sensor_guid = None, data_name = None, max_items = 5):
         new_queue = asyncio.Queue(max_items)
         new_subscriber = dict(sensor_guid=sensor_guid, data_name=data_name, queue = new_queue)
         self.subscribers += [new_subscriber]

         return new_queue

    async def send_to_subscribers(self, sensor_guid, data):
        def put_to_possibly_full_queue(queue, data):
            if queue.full():
                queue.get_nowait()
            queue.put_nowait(data)

        for sub in self.subscribers:
            if not sub['sensor_guid'] or sub['sensor_guid'] == sensor_guid:
                if not sub['data_name']:
                    # if no data_name is given, send the whole thing!
                    put_to_possibly_full_queue(sub['queue'], data)
                elif sub['data_name'] in data:
                    put_to_possibly_full_queue(sub['queue'], data[sub['data_name']])





def test_json_sensor_server():
    from mode import Worker

    supervisor = OneForOneSupervisor()
    json_sensor_server = JsonSensorServer(\
            port_greps = ['Leonardo']
        )


    class DataReader(Service):
        # @Service.timer(5.0)
        # async def interfere(self):
        #     await json_sensor_server.crash(RuntimeError('Something went wrong... Hehehe...'))
        #     self.log.info('poll')

        async def handle_data(self, sender, data={}, aggregated_data={}, **kwds):
            self.log.info(f'DataReader: Aggregated data is now: {repr(aggregated_data)}')
            
    data_reader = DataReader()
    json_sensor_server.on_data_update.connect(data_reader.handle_data)

    supervisor.add(json_sensor_server)
    supervisor.add(data_reader)

    # Worker(supervisor, loglevel="debug").execute_from_commandline()
    Worker(supervisor, loglevel="debug").execute_from_commandline()

if __name__ == '__main__':
    test_json_sensor_server()
  
