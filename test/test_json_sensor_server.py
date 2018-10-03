import sys
sys.path.append('.')
sys.path.append('..')

from json_sensor import *

def test_json_sensor_server():
    from mode import Worker

    supervisor = OneForOneSupervisor()
    json_sensor_server = JsonSensorServer(\
            port_greps = ['Arduino', 'Trinket M0']
        )


    class DataReader(Service):
        async def handle_data(self, sender, data={}, aggregated_data={}, **kwds):
            self.log.info(f'DataReader: Aggregated data is now: {repr(aggregated_data)}')
            
    data_reader = DataReader()
    json_sensor_server.on_data_update.connect(data_reader.handle_data)

    supervisor.add(json_sensor_server)
    supervisor.add(data_reader)

    # Worker(supervisor, loglevel="debug").execute_from_commandline()
    Worker(supervisor, loglevel="info").execute_from_commandline()

if __name__ == '__main__':
    test_json_sensor_server()
  
