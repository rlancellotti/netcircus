import netcircus_paths
from host import Host
from switch import Switch
from cable import Cable
import os
import threading
import time
import json

class Network:
    def __init__(self, name):
        self.name = name
        self.save_path = netcircus_paths.SAVE_PATH + '/' + name
        self.hosts = []
        self.switches = []
        self.cables = []
    def create_project_path(self):
        if os.path.exists(self.save_path):
            decision = input("il progetto " + self.name + " esiste gia', sovrascrivere? si/no ")
            if decision == 'no':
                self.name = input("allora inserire altro nome.. ")
                self.save_path = netcircus_paths.SAVE_PATH + '/' + self.name
            elif decision == 'si':
                os.remove(self.save_path)
            else:
                exit(1)
        os.makedirs(self.save_path)

    def add(self, obj):
        if type(obj) == Host:
            self.hosts.append(obj)
            return
        if type(obj) == Switch:
            self.switches.append(obj)
            return
        if type(obj) == Cable:
            self.cables.append(obj)
            return

    def start_up(self):

        for c in self.hosts + self.switches:
            t = threading.Thread(target=c.launch, args=())
            t.daemon = True
            t.start()
            time.sleep(0.2)
        # FIXME: must wait for host to be readycomplete their startup
        #time.sleep(5)
        for c in self.cables:
            if c.type == 'straight':
                c.make_host_switch_connection()
            else:
                if type(c.A) == Host:
                    print('collegamento Host to Host impossibile, mettici uno switch in mezzo :-)')
                else:
                    t = threading.Thread(target=c.make_switches_connection, args=(), daemon=True)
                    t.start()

    def shutdown(self):
        for c in self.hosts + self.switches:
            if c.check():
                print('spengo in modo pulito ' + c.name)
                c.shutdown()

    def poweroff(self):
        for c in self.hosts + self.switches:
            if c.check:
                print('chiudo forzatamente ' + c.name)
                c.halt()


def save(net, path, configuration):
    net.create_project_path()

    list_host = []
    list_switch = []
    list_cable = []

    for h in net.hosts:
        h_dict = {'name': h.name,
                  'label': h.label,
                  'fs': h.fs,
                  'kernel': h.kernel,
                  'n_ports': h.n_ports,
                  'mem': h.mem,
                  'n_disks': h.n_disks}
        list_host.append(h_dict)

    for s in net.switches:
        s_dict = {'name': s.name,
                  'label': s.label,
                  'n_ports': s.n_ports,
                  'is_hub,': s.is_hub,
                  'terminal': s.terminal}
        list_switch.append(s_dict)

    for c in net.cables:
        c_dict = {'name': c.name,
                  'A': c.A.name,
                  'port_A': c.port_A,
                  'B': c.B.name,
                  'port_B': c.port_B}
        list_cable.append(c_dict)

    network_dict = {'network_name': net.name,
                    'host_list': list_host,
                    'switch_list': list_switch,
                    'cable_list': list_cable}

    f_name = net.name + '.json'
    with open(f_name, 'w') as f:
        json.dump(network_dict, f, indent=3)
    f.close()

    os.system('mv ' + f_name + ' /tmp/')

    file_cow = ''
    if configuration is True:
        file_cow = '/tmp/' + net.name + '*.cow'

    os.system('tar -cSzvf ' + path + '/arc_' + net.name + '_SimNet.tgz -P ' + file_cow +
              ' /tmp/' + f_name + ' --atime-preserve')


def load(arc_file_path):
    """

    :type arc_file_path: String
    :rtype: Network
    """

    print('arc_file path: ' + arc_file_path)
    arc_name = arc_file_path.split('/')
    arc_name = arc_name[-1]
    print('arc_name: ' + arc_name)
    path = arc_file_path[:-len(arc_name)]
    print('path: ' + path)

    # os.makedirs(path + '/bho')

    com = 'tar -P -xvzf ' + arc_file_path + ' -C ' + path
    print(com)
    os.system(com)

    # with open(arc_file_path, 'r') as f:
      #  data = json.load(f)
    return