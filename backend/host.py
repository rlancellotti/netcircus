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

    def __init__(self, network, data):
        super().__init__(data['id'])
        self.network=network
        self.id=data['id'] 
        self.name = data['name'] if 'name' in data.keys() else 'unnamed'
        self.description = data['description'] if 'description' in data.keys() else ''
        self.kernel = data['kernel'] if 'kernel' in data.keys() else netcircus_paths.get_kernels()[0]
        self.fs = data['filesystem'] if 'filesystem' in data.keys() else netcircus_paths.get_filesystems()[0]
        self.cow = data['cow'] if 'cow' in data.keys() else f'{netcircus_paths.WORKAREA}/{self.id}.cow'
        self.mem = int(data['mem']) if 'mem' in data.keys() else '96'
        self.x = data['x' ] if 'x' in data.keys() else '0.0'
        self.y = data['y' ] if 'y' in data.keys() else '0.0'
        self.width = data['width' ] if 'width' in data.keys() else '0.0'
        self.height = data['height' ] if 'height' in data.keys() else '0.0'
        self.check_cow(self.cow, self.fs)
        self.ready=False
        self.console = self.id + '_cmd'
        self.console_signals['stop'] = 'cad'
        self.console_signals['halt'] = 'halt'
        self.console_signals['check'] = 'version > /dev/null 2>&1'
        self.command_queue=[]
        self.ready_socket_name=f'{netcircus_paths.WORKAREA}/socket_ready_{self.id}.s'
        self.set_ready_socket()
        self.network.add(self)

    def get_cmdline(self):
        cmdline=self.kernel + f' mem={int(self.mem)}M ubd0={self.cow},{self.fs} umid={self.console} mconsole=notify:{self.ready_socket_name} hostname={self.name}'
        print(cmdline)
        return cmdline

    def update(self, data):
        if 'name' in data.keys(): self.name=data['name']
        if 'description' in data.keys(): self.description=data['description']
        if 'mem' in data.keys(): self.mem = data['mem'] 
        if 'kernel' in data.keys(): self.kernel=data['kernel']
        if 'filesystem' in data.keys(): self.fs=data['filesystem']
        if 'cow' in data.keys(): self.cow=data['cow']
        if 'x' in data.keys(): self.x=data['x']
        if 'y' in data.keys(): self.y=data['y']
        if 'width' in data.keys(): self.width=data['width']
        if 'height' in data.keys(): self.height=data['height']
        print(self.dump())

    def dump(self) -> dict:
        rv={}
        rv['id']=self.id
        rv['name']=self.name
        rv['description']=self.description
        rv['kernel']=self.kernel
        rv['filesystem']=self.fs
        rv['cow']=self.cow
        rv['mem']=self.mem
        rv['x']=self.x
        rv['y']=self.y
        rv['width']=self.width
        rv['height']=self.height
        return rv

    def clean(self):
        if os.path.exists(self.cow):
            os.remove(self.cow)

    def check_cow(self, cow, fs):
        if os.path.exists(cow) and (os.path.getmtime(fs) > os.path.getmtime(cow)):
            self.log(logging.WARNING, f'backing file {fs} is newer than cow {cow}')
            os.remove(cow)

    def wait_ready(self):
        self.log(logging.DEBUG, 'entering call to wait_ready')
        data = self.ready_sock.recv(1024)
        #hex_dump(data)
        #self.console=data[16:-1].decode('ascii')
        #print(self.console)
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
        print(self.ready_socket_name)
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
            if not command.startswith(self.console_signals['check']):
                self.log(logging.DEBUG, f'queueing command {command}')
            self.command_queue.append(command)
            return None
        rv=False
        if os.system(f'uml_mconsole {self.console} {command}') == 0:
            rv=True
        self.log_command(command, rv)
        return rv
    
    def stop(self):
        os.remove(self.ready_socket_name)

    def connect_to_switch(self, host_port, component, switch_port):
        time.sleep(5)
        self.command(f'config eth{host_port}=vde,{netcircus_paths.WORKAREA}/{component},{Host.get_mac()},{switch_port}')

def hex_dump(data):
    for i in range(len(data)):
        print(i, data[i], chr(data[i]))