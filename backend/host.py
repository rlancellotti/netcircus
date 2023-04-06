import netcircus_paths
import component
import socket
import os
import time
import threading

class Host(component.Component):
    mac_counter = 0
    mac_prefix = '02:04:06'
    @classmethod
    def get_mac(cls) -> str:
        Host.mac_counter += 1
        return  '%s:%02x:%02x:%02x' % (Host.mac_prefix, Host.mac_counter // (256*256), Host.mac_counter // 256, Host.mac_counter % 256)

    def __init__(self, project_name, host_name, label, mem=96, ndisks=1):
        """
        :param fs: filesystem
        :param kernel: kernel linux per UML
        :param console: name_cmd, permette comunicazione tramite uml_mconsole
        :param n_ports: numero di porte
        :param mem: memoria
        :param n_disk: numero di dischi da montare sull'host

        """
        super().__init__()
        self.ready=False
        self.project = project_name
        self.name = host_name
        self.label = label
        self.n_disks = ndisks
        self.mem = mem

        self.fs = netcircus_paths.FS1
        self.kernel = netcircus_paths.KER1
        self.console = self.name + '_cmd'

        self.console_signals['stop'] = 'cad'
        self.console_signals['halt'] = 'halt'
        self.console_signals['check'] = 'version > /dev/null 2>&1'
        self.command_queue=[]
        self.cmdline = self.kernel + f' mem={self.mem}M '

        self.ready_socket_name=f'{netcircus_paths.WORKAREA}/socket_ready_{self.name}.s'
        for i in range(ndisks):
            disk_name = f'{self.project}_{self.name}_disk{i}'
            self.cmdline = self.cmdline + f'ubd{i}={netcircus_paths.WORKAREA}/{disk_name}.cow,{self.fs} '
            self.check_cow(f'{netcircus_paths.WORKAREA}/{disk_name}.cow', self.fs)
        self.cmdline = self.cmdline + f'umid={self.console} mconsole=notify:{self.ready_socket_name} hostname={self.name}'
        self.set_ready_socket()
        print(self.cmdline)

    def check_cow(self, cow, fs):
        if os.path.exists(cow) and (os.path.getmtime(fs) > os.path.getmtime(cow)):
            print(f'backing file {fs} is newer than cow {cow}')
            os.remove(cow)
    
    def wait_ready(self):
        print('entering call to wait_ready')
        data = self.ready_sock.recv(1024)
        #self.console=data[16:].decode('utf-8')
        #print (self.console)
        self.ready=True
        time.sleep(1)
        for c in self.command_queue:
            self.command(c)
        time.sleep(1)
        print('end call to set_ready')

    def set_ready_socket(self):
        if os.path.exists(self.ready_socket_name):
            os.remove(self.ready_socket_name)
        self.ready_sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        print(self.ready_socket_name)
        self.ready_sock.bind(self.ready_socket_name)
        print(f'call to set_ready_socket on {str(self.ready_sock)}')
        threading.Thread(target=self.wait_ready, daemon=True).start()

    def log_command(self, command, success):
        adj='successful' if success else 'failed'
        #print(f'{adj} command: "{command}"')
        if not command.startswith('version'):
            print(f'{adj} command: "{command}"')

    def command(self, command):
        if not self.ready:
            if not command.startswith('version'):
                print(f'queueing command {command}')
            self.command_queue.append(command)
            return None
        rv=False
        if os.system(f'uml_mconsole {self.console} {command}') == 0:
            rv=True
        self.log_command(command, rv)
        return rv

    def connect_to_switch(self, host_port, component, switch_port):
        self.command(f'config eth{host_port}=vde,{netcircus_paths.WORKAREA}/{component},{Host.get_mac()},{switch_port}')
