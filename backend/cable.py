import netcircus_paths
from host import Host
from switch import Switch
import os

class Cable:
    def __init__(self, network, name=None, endpoint_A=None, port_A=None, endpoint_B=None, port_B=None, dump=None):
        """

        :param i: numero cavo
        :param A: Componente all'estremo A, sempre Host se cavo straight
        :param port_A: porta del Componente A alla quale collegare il cavo
        :param B: Componente all'estremo B, sempre Switch se cavo straight
        :param port_B: porta del Componente B alla quale collegare il cavo

        """
        if dump is None:
            self.init_from_parameters(name, endpoint_A, port_A, endpoint_B, port_B)
        else:
            self.init_from_dump(dump, network)
        network.add(self)

    def init_from_dump(self, dump, network):
        self.name = dump['name']
        self.type = dump['type']
        self.A = dump['endpoint_A'] # FIXME: must retrieve object from ntwork!
        self.port_A = dump['port_A']
        self.B = dump['endpoint_B'] # FIXME: must retrieve object from ntwork!
        self.port_B = dump['port_B']

    def init_from_parameters(self, name, endpoint_A, port_A, endpoint_B, port_B):
        self.type = 'straight'
        self.name = name
        self.A = endpoint_A
        self.B = endpoint_B
        self.port_A = port_A
        self.port_B = port_B
        self.check_connection()
        self.name = f'{self.type}_{self.name}'

    def check_connection(self):
        if type(self.A) == type(self.B):
            self.type = 'cross'
        else:
            if type(self.A) != Host:
                (self.A, self.port_A, self.B, self.port_B) = (self.B, self.port_B, self.A, self.port_A)

    def dump(self) -> dict:
        rv={}
        rv['name']=self.name
        rv['type']=self.type
        rv['endpoint_A']=self.A.name
        rv['port_A']=self.port_A
        rv['endpoint_B']=self.B.name
        rv['port_B']=self.port_B
        return rv

    def make_switches_connection(self):
        os.system(f'dpipe vde_plug {netcircus_paths.WORKAREA}/{self.A.name} = vde_plug {netcircus_paths.WORKAREA}/{self.B.name}')

    def make_host_switch_connection(self):
        self.A.connect_to_switch(self.port_A, self.B.name, self.port_B)
