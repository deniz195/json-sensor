import sys
sys.path.append('.')
sys.path.append('..')

from json_sensor import *
from mode import Worker

async def handle_data(sender, data={}, aggregated_data={}, **kwds):
    print(f'Aggregated data is now: {repr(aggregated_data)}')
        
json_sensor_server = JsonSensorServer(port_greps = ['Arduino'])
json_sensor_server.on_data_update.connect(handle_data)

# Worker(json_sensor_server, loglevel="debug").execute_from_commandline()
Worker(json_sensor_server, loglevel="info").execute_from_commandline()
