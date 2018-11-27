import time
import threading
import os
import json

PATH = os.path.expanduser('~/SimNet')
SAVE_PATH = os.path.expanduser('~/SimNet/Projects')
RESOURCE_PATH = os.path.expanduser('~/SimNet/Resources')
FS1 = RESOURCE_PATH + '/rootfs.ext4'
KER1 = RESOURCE_PATH + '/linux'
KER2 = RESOURCE_PATH + '/linux-3.18.20-mod'
KER3 = RESOURCE_PATH + '/linux-4.10-mod'


class Controller(threading.Thread):
    def __init__(self, network):
        super().__init__()
        self.active = True
        self.net = network

        self.hosts_states = {}
        for h in network.hosts:
            self.hosts_states[h] = 'closed'

        self.switches_states = {}
        for s in network.switches:
            self.switches_states[s] = 'closed'

    def check_start(self):
        time.sleep(1)
        for h in self.net.hosts:
            if not h.check():
                print(h.name + ' non è partito correttamente')
                return False
            else:
                self.hosts_states[h] = 'opened'
                print(h.name + " è partito correttamente")
        for s in self.net.switches:
            if not s.check():
                print(s.name + ' non è partito correttamente')
                return False
            else:
                self.switches_states[s] = 'opened'
                print(s.name + " è partito correttamente")
        return True

    def run(self):
        print('inizia il controllo')
        while self.active:
            time.sleep(1)
            for h in self.hosts_states:
                if h.check():
                    self.hosts_states[h] = 'opened'
                else:
                    if self.hosts_states[h].__eq__('opened'):
                        print('(host) ' + h.name + ' chiuso')
                        self.hosts_states[h] = 'closed'

            for s in self.switches_states:
                if s.check():
                    self.switches_states[s] = 'opened'
                else:
                    if self.switches_states[s].__eq__('opened'):
                        print('(switch) ' + s.name + ' chiuso')
                        self.switches_states[s] = 'closed'
        return

    def set_active(self, active):
        self.active = active


class Component:
    def __init__(self):
        """

        :param project_name: nome del progetto all'interno del quale si trova il dispositivo
        :param name: nome, per semplicita': 'Host'/'Switch' + cardinalià
        :param label: etichetta, non utilizzato

        """
        self.project_name = ''
        self.name = ''
        self.label = ''
        self.n_ports = 0
        self.console = ''

        self.console_signals = {'stop': '',
                                'halt': '',
                                'check': ''}
        self.configuration = ''

    def launch(self):
        os.system("xterm -T " + self.name + " -e \"" + self.configuration + "\"")

    def command(self, command):
        pass

    def check(self):
        r = self.command(self.console_signals['check'])
        return r

    def shutdown(self):
        self.command(self.console_signals['stop'])

    def halt(self):
        self.command(self.console_signals['halt'])


class Host(Component):
    def __init__(self, project_name, name, label, n_ports, mem, n_disks):
        """

        :param fs: filesystem
        :param kernel: kernel linux per UML
        :param console: name_cmd, permette comunicazione tramite uml_mconsole
        :param n_ports: numero di porte
        :param mem: memoria
        :param n_disk: numero di dischi da montare sull'host

        """
        super().__init__()
        self.project = project_name
        self.name = name
        self.label = label
        self.n_ports = n_ports
        self.mem = mem
        self.n_disks = n_disks

        self.fs = FS1
        self.kernel = KER1
        self.console = self.name + '_cmd'

        self.console_signals['stop'] = 'cad'
        self.console_signals['halt'] = 'halt'
        self.console_signals['check'] = 'version > /dev/null 2>&1'

        self.configuration = self.kernel + ' mem=' + str(self.mem) + 'm '

        for i in range(n_disks):
            disk = self.project + '_' + self.name + '_disk' + str(i)
            self.configuration = self.configuration + 'ubd' + str(i) + '=/tmp/' + disk + '.cow,' + self.fs + ' '
            self.configuration = self.configuration + 'umid=' + self.console

    def command(self, command):
        if os.system("uml_mconsole " + self.console + " " + command) == 0:
            return True
        return False

    def connect_to_switch(self, myPort, component, hisPort):
        self.command('config eth' + str(myPort) + '=vde,/tmp/' + component + ',,' + str(hisPort))


class Switch(Component):
    def __init__(self, name, label, n_ports, is_hub, terminal):
        """

        :param n_ports: numero di porte
        :param ishub: True se funziona da Hub
        :param terminal: False se si vuole nascondere il terminal

        """
        super().__init__()
        self.name = name
        self.label = label
        self.n_ports = n_ports
        self.is_hub = is_hub
        self.terminal = terminal

        self.console = self.name + '_cmd'

        self.console_signals['stop'] = 'shutdown'
        self.console_signals['check'] = 'showlist > /dev/null 2>&1'

        daemon = ''
        hub = ''
        if not self.terminal:
            daemon = '-d '
        if self.is_hub:
            hub = '-x '
        self.configuration = "vde_switch " + daemon + "-n " + str(self.n_ports) + " " + hub + "-s /tmp/" + self.name +\
                             " --mgmt /tmp/" + self.console + ".mgmt"

    def command(self, command):
        # 65280 exit status comando unixcmd
        if os.system("unixcmd -s /tmp/" + self.console + ".mgmt -f /etc/vde2/vdecmd " + command) == 65280:
            return True
        return False

    def halt(self):
        os.system("pgrep -f /tmp/" + self.name + " | xargs kill -TERM")

    def check(self):
        return os.path.exists('/tmp/' + self.console + '.mgmt')


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
        os.system("dpipe vde_plug /tmp/" + self.A.name + " = vde_plug /tmp/" + self.B.name)

    def make_host_switch_connection(self):
        self.A.connect_to_switch(self.port_A, self.B.name, self.port_B)


class Network:

    def __init__(self, name):
        self.name = name
        self.save_path = SAVE_PATH + '/' + name
        self.hosts = []
        self.switches = []
        self.cables = []

    def create_project_path(self):
        if os.path.exists(self.save_path):
            decision = input("il progetto " + self.name + " esiste gia', sovrascrivere? si/no ")
            if decision == 'no':
                self.name = input("allora inserire altro nome.. ")
                self.save_path = SAVE_PATH + '/' + self.name
            elif decision == 'si':
                os.remove(self.save_path)
            else:
                exit(1)
        os.makedirs(self.save_path)

    def add_host(self, host):
        self.hosts.append(host)

    def add_switch(self, switch):
        self.switches.append(switch)

    def add_cable(self, cable):
        self.cables.append(cable)

    def start_up(self):

        for c in self.hosts + self.switches:
            t = threading.Thread(target=c.launch, args=())
            t.daemon = True
            t.start()
            time.sleep(0.2)

        for c in self.cables:
            if c.type == 'straight':
                c.make_host_switch_connection()
            else:
                if type(c.A) == Host:
                    print('collegamento Host to Host impossibile, mettici uno switch in mezzo :-)')
                else:
                    t = threading.Thread(target=c.make_switches_connection, args=())
                    t.daemon = True
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



















