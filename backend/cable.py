import netcircus_paths
from host import Host
from switch import Switch
import os

class Cable:
    def __init__(self, network, id=None, name=None, endpoint_A=None, port_A=None, endpoint_B=None, port_B=None, dump=None):
        """

        :param i: numero cavo
        :param A: Componente all'estremo A, sempre Host se cavo straight
        :param port_A: porta del Componente A alla quale collegare il cavo
        :param B: Componente all'estremo B, sempre Switch se cavo straight
        :param port_B: porta del Componente B alla quale collegare il cavo

        """
        if dump is None:
            self.init_from_parameters(network,name, id, endpoint_A, port_A, endpoint_B, port_B)
        else:
            self.init_from_dump(dump, network)
        network.add(self)

    def init_from_dump(self, dump, network):
        self.network=network
        self.name = dump['name']
        self.type = dump['type']
        self.A = network.get_element_by_id(dump['endpoint_A'])
        self.port_A = dump['port_A']
        self.B = network.get_element_by_id(dump['endpoint_B'])
        self.port_B = dump['port_B']
        self.id=dump['id']

    def init_from_parameters(self, network, name, id, endpoint_A, port_A, endpoint_B, port_B):
        self.network=network
        self.type = 'straight'
        self.A = endpoint_A
        self.B = endpoint_B
        self.port_A = port_A
        self.port_B = port_B
        self.check_connection()
        self.id=id
        self.name = f'{self.type}_{self.id}'
        

    def check_connection(self):
        if type(self.A) == type(self.B):
            self.type = 'cross'
        else:
            if type(self.A) != Host:
                (self.A, self.port_A, self.B, self.port_B) = (self.B, self.port_B, self.A, self.port_A)

    def dump(self) -> dict:
        rv={}
        rv['name']=self.name
        rv['id']=self.id
        rv['type']=self.type
        rv['endpoint_A']=self.A.id
        rv['port_A']=self.port_A
        rv['endpoint_B']=self.B.id
        rv['port_B']=self.port_B
        return rv
    
    def update(self, data):
        if 'a_port' in data.keys(): self.port_A=data['a_port']
        if 'b_port' in data.keys(): self.port_B=data['b_port']
        print(self.dump())

    def make_switches_connection(self):
        os.system(f'dpipe vde_plug {netcircus_paths.WORKAREA}/{self.A.name} = vde_plug {netcircus_paths.WORKAREA}/{self.B.name}')

    def make_host_switch_connection(self):
        self.A.connect_to_switch(self.port_A, self.B.name, self.port_B)
