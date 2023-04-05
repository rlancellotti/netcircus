import netcircus_paths
import component
import socket

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

        self.socketname=f'/tmp/socket_ready_{self.name}.s'
        for i in range(ndisks):
            disk = self.project + '_' + self.name + '_disk' + str(i)
            self.cmdline = self.cmdline + f'ubd{str(i)}=/tmp/{disk}.cow,{self.fs} '
        self.cmdline = self.cmdline + f'umid={self.console} con1=xterm mconsole=notify:{self.socketname} hostname={self.name}'
        self.set_ready_socket()
        print(self.cmdline)

    def wait_ready(self):
        print('entering call to wait_ready')
        data = self.sock.recv(1024)
        print(data[16:].decode('utf-8'))
        self.ready=True
        time.sleep(1)
        for c in self.command_queue:
            self.command(c)
        time.sleep(1)
        print('end call to set_ready')

    def set_ready_socket(self):
        if os.path.exists(self.socketname):
            os.remove(self.socketname)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.sock.bind(self.socketname)
        print(f'call to set_ready_socket on {str(self.sock)}')
        threading.Thread(target=self.wait_ready, daemon=True).start()
        #asyncio.run(asyncio.start_server(self.set_ready, sock=sock))

    def log_command(self, command, success):
        adj='successful' if success else 'failed'
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

    def connect_to_switch(self, myPort, component, hisPort):
        self.command(f'config eth{str(myPort)}=vde,/tmp/{component},{Host.get_mac()},{str(hisPort)}')
