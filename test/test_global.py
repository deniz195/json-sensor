import sys
sys.path.append('.')
sys.path.append('..')

from json_sensor import *
import json_sensor

def test_json_sensor_server():
    from mode import Worker

    supervisor = OneForOneSupervisor()
    json_sensor.initialize_server(\
        port_greps = ['Arduino', 'Trinket']
    )

    class DataReader(Service):
        async def handle_data(self, sender, data={}, aggregated_data={}, **kwds):
            self.log.info(f'DataReader: Aggregated data is now: {repr(aggregated_data)}')

        @Service.task
        async def read_adc1(self):
            while not self.should_stop:
                data = await self.adc_queue1.get()
                self.log.info(f'DataReader: New ADC1 value: {data}')

        @Service.task
        async def read_adc2(self):
            while not self.should_stop:
                data = await self.adc_queue2.get()
                self.log.info(f'DataReader: New ADC2 value: {data}')

            
    data_reader = DataReader()
    data_reader.adc_queue1 = json_sensor.get_server().create_subscriber_queue('btrn-adc-sensor-0002', 'adc_ch01')
    data_reader.adc_queue2 = json_sensor.get_server().create_subscriber_queue('btrn-adc-sensor-0002', 'adc_ch23')

    json_sensor.get_server().on_data_update.connect(data_reader.handle_data)

    supervisor.add(json_sensor.get_server())
    supervisor.add(data_reader)

    # Worker(supervisor, loglevel="debug").execute_from_commandline()
    Worker(supervisor, loglevel="info").execute_from_commandline()

if __name__ == '__main__':
    test_json_sensor_server()
  
