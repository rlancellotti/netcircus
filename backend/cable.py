import netcircus_paths
from host import Host
from switch import Switch
import os

class Cable:
    def __init__(self, name, A, port_A, B, port_B):
        """

        :param i: numero cavo
        :param A: Componente all'estremo A, sempre Host se cavo straight
        :param port_A: porta del Componente A alla quale collegare il cavo
        :param B: Componente all'estremo B, sempre Switch se cavo straight
        :param port_B: porta del Componente B alla quale collegare il cavo

        """
        self.type = 'straight'
        self.A = A
        self.B = B
        self.port_A = port_A
        self.port_B = port_B
        if type(A) == type(B):
            self.type = 'cross'
        else:
            if type(A) != Host:
                self.A = B
                self.B = A
                self.port_A = port_B
                self.port_B = port_A
        self.name = self.type + '_' + name

    def make_switches_connection(self):
        os.system(f'dpipe vde_plug {netcircus_paths.WORKAREA}/{self.A.name} = vde_plug {netcircus_paths.WORKAREA}/{self.B.name}')

    def make_host_switch_connection(self):
        self.A.connect_to_switch(self.port_A, self.B.name, self.port_B)
