import sys
sys.path.append('.')
sys.path.append('..')

from json_sensor import *
import json_sensor
from mode import Worker

async def handle_data(sender, data={}, aggregated_data={}, **kwds):
    print(f'Aggregated data is now: {repr(aggregated_data)}')


supervisor = OneForOneSupervisor()
json_sensor.initialize_server(\
    port_greps = []
)
# json_sensor_server.on_data_update.connect(handle_data)

class PortReporter(Service):
    async def on_start(self):
        # await self.print_known_ports()
        await json_sensor.get_server().get_all_port_grepable()

    @Service.timer(5)
    async def print_known_ports(self):
        await json_sensor.get_server().get_all_port_grepable()
        
port_reporter = PortReporter()
supervisor.add(json_sensor.get_server())
supervisor.add(port_reporter)

# Worker(supervisor, loglevel="debug").execute_from_commandline()
Worker(supervisor, loglevel="info").execute_from_commandline()

