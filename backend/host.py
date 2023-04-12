import netcircus_paths
from component import Component
import socket
import os
import time
import threading
import logging

class Host(Component):
    mac_counter = 0
    mac_prefix = '02:04:06'
    @classmethod
    def get_mac(cls) -> str:
        Host.mac_counter += 1
        return  '%s:%02x:%02x:%02x' % (Host.mac_prefix, Host.mac_counter // (256*256), Host.mac_counter // 256, Host.mac_counter % 256)

    def __init__(self, network, name=None, label=None, mem=96, dump=None):
        super().__init__(name if name is not None else dump['name'])
        self.network=network
        if dump is None:
            self.init_from_parameters(network, name, label, mem)
        else:
            self.init_from_dump(dump)
        self.check_cow(self.cow, self.fs)
        self.ready=False
        self.console = self.name + '_cmd'
        self.console_signals['stop'] = 'cad'
        self.console_signals['halt'] = 'halt'
        self.console_signals['check'] = 'version > /dev/null 2>&1'
        self.command_queue=[]
        self.ready_socket_name=f'{netcircus_paths.WORKAREA}/socket_ready_{self.name}.s'
        self.set_ready_socket()
        self.cmdline = self.kernel + f' mem={self.mem}M ubd0={self.cow},{self.fs} umid={self.console} mconsole=notify:{self.ready_socket_name} hostname={self.name}'
        self.log(logging.DEBUG, self.cmdline)
        self.network.add(self)

    def init_from_dump(self, dump):
        self.name = dump['name']
        self.label = dump['label']
        self.kernel = dump['kernel']
        self.fs = dump['filesystem']
        self.cow = dump['cow']
        self.mem = dump['mem']

    def init_from_parameters(self, network, name, label, mem):
        self.network = network
        self.name = name
        self.label = label
        self.kernel = netcircus_paths.KER1
        self.fs = netcircus_paths.FS1
        self.cow=f'{netcircus_paths.WORKAREA}/{self.name}_0.cow'
        self.mem = mem

    def dump(self) -> dict:
        rv={}
        rv['name']=self.name
        rv['label']=self.label
        rv['kernel']=self.kernel
        rv['filesystem']=self.fs
        rv['cow']=self.cow
        rv['mem']=self.mem
        return rv

    def check_cow(self, cow, fs):
        if os.path.exists(cow) and (os.path.getmtime(fs) > os.path.getmtime(cow)):
            self.log(logging.WARNING, f'backing file {fs} is newer than cow {cow}')
            os.remove(cow)
    
    def wait_ready(self):
        self.log(logging.DEBUG, 'entering call to wait_ready')
        data = self.ready_sock.recv(1024)
        #self.console=data[16:].decode('utf-8')
        #print (self.console)
        self.ready=True
        time.sleep(1)
        for c in self.command_queue:
            self.command(c)
        time.sleep(1)
        self.log(logging.DEBUG, 'end call to set_ready')

    def set_ready_socket(self):
        if os.path.exists(self.ready_socket_name):
            os.remove(self.ready_socket_name)
        self.ready_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.log(logging.DEBUG, self.ready_socket_name)
        self.ready_sock.bind(self.ready_socket_name)
        self.log(logging.DEBUG, f'call to set_ready_socket on {str(self.ready_sock)}')
        threading.Thread(target=self.wait_ready, daemon=True).start()

    def log_command(self, command, success):
        adj='successful' if success else 'failed'
        #print(f'{adj} command: "{command}"')
        #if not command.startswith('version'):
        self.log(logging.DEBUG, f'{adj} command: "{command}"')

    def command(self, command):
        if not self.ready:
            if not command.startswith('version'):
                self.log(logging.DEBUG, f'queueing command {command}')
            self.command_queue.append(command)
            return None
        rv=False
        if os.system(f'uml_mconsole {self.console} {command}') == 0:
            rv=True
        self.log_command(command, rv)
        return rv

    def connect_to_switch(self, host_port, component, switch_port):
        self.command(f'config eth{host_port}=vde,{netcircus_paths.WORKAREA}/{component},{Host.get_mac()},{switch_port}')
