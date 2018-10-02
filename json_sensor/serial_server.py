import asyncio
import logging
import mode
import janus
import json
import time

from mode import Service, OneForOneSupervisor, Signal, SignalT

import serial
from serial.threaded import LineReader, ReaderThread
import threading

import enum

import serial
import serial.tools.list_ports as list_ports

from json_sensor.robust_serial_service import *
from json_sensor.json_sensor import *






async def default_port_reader_factory(port_info):
    print(f'default_port_reader_factory on {port_info.device}')
    connection = RobustSerialService(\
            device = port_info.device,
            baudrate = 9600,
            timeout = 10,
            protocol_factory = JanusLineReader
        )
    return connection

class USBSerialServer(Service):

    def __init__(self,
                 port_reader_factory=default_port_reader_factory,
                 port_greps = [],
                *args, **kwds):

        super().__init__(*args, **kwds)

        self.port_reader_factory = port_reader_factory
        self.port_greps = port_greps 

        self.known_ports = {}
        self.knowledge_timeout = 10


    async def grep_ports(self):
        ports = []
        for regex in self.port_greps:
            ports += list_ports.grep(regex)

        return ports

    def get_port_hash(self, port_info):
        ''' Calculates a hash for a pyserial port_info object '''
        return hash(frozenset(port_info.__dict__.items()))

    def is_port_reader_service_running(self, hash_value):
        known_port = self.known_ports.get(hash_value, None)
        if known_port is None:
            return False
        else:
            reader_service = known_port['reader_service']
            return reader_service.state in ['init', 'running']


    async def register_known_port(self, port_info):
        self.log.debug(f'Registering port {port_info.device}')

        hash_value = self.get_port_hash(port_info)

        start_new_reader_service = True
        
        # check if there is a reader_service running!
        if self.is_port_reader_service_running(hash_value):
            start_new_reader_service = False
            self.log.debug(f'Reader service on {port_info.device} is still running! All good.')       

        # write down in known_ports registry
        new_known_port = dict(\
                time=time.monotonic(), 
                port_info=port_info.__dict__.copy(), 
            )

        # start reader service if necessary
        if start_new_reader_service:
            self.log.debug(f'Starting reader service on {port_info.device}!')
            reader_service = await self.port_reader_factory(port_info)
            await self.add_runtime_dependency(reader_service)
            new_known_port['reader_service'] = reader_service

        if hash_value not in self.known_ports:
            self.known_ports[hash_value] = new_known_port
        else: 
            self.known_ports[hash_value].update(new_known_port)


    async def delete_known_port(self, port_info, hash_value=None):
        if hash_value is None:
            hash_value = self.get_port_hash(port_info)

        if hash_value in self.known_ports:
            if port_info is None:
                port_info_device = self.known_ports[hash_value]['port_info']['device']
            else:
                port_info_device = port_info.device
        
        if self.is_port_reader_service_running(hash_value):
            self.log.debug(f'Reader service still running. Not deleting {port_info_device}!')
        else:
            self.log.debug(f'Deleting port {port_info_device}')
            del self.known_ports[hash_value]


    def is_port_known(self, port_info, hash_value=None):
        if hash_value is None:
            hash_value = self.get_port_hash(port_info)

        now = time.monotonic()

        known_port = self.known_ports.get(hash_value, None)
        if known_port is None:
            return False
        elif self.is_port_reader_service_running(hash_value):
            return True
        elif now - self.known_ports[hash_value]['time'] > self.knowledge_timeout:
            return False
        else:
            return True

    async def remove_unknown_ports(self):
        port_hashs = list(self.known_ports.keys())
        unknown_ports = [port_hash for port_hash in port_hashs if not self.is_port_known(None, hash_value=port_hash)]
        for port_hash in port_hashs:
            if not self.is_port_known(None, hash_value=port_hash):
                await self.delete_known_port(None, hash_value=port_hash)      

    @Service.timer(1.0)
    async def check_for_new_ports(self):
        await self.remove_unknown_ports()

        all_ports = await self.grep_ports()
        for port in all_ports:
            if not self.is_port_known(port):
                await self.register_known_port(port)



def test_usb_serial_server():
    from mode import Worker

    supervisor = OneForOneSupervisor()
    serial_server = USBSerialServer(\
            port_greps = ['Leonardo']
        )

    supervisor.add(serial_server)

    # Worker(supervisor, loglevel="debug").execute_from_commandline()
    Worker(supervisor, loglevel="debug").execute_from_commandline()

if __name__ == '__main__':
    test_usb_serial_server()
  
