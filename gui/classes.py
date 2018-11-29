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


class Component:
    def __init__(self):
        self.name = ""
        self.label = ""
        self.state = ""
        self.n_ports = 0

    def set_name(self, name):
        self.name = name

    def set_label(self, label):
        self.label = label

    def set_n_ports(self, n):
        self.n_ports = n

    def run(self, path):
        pass

    def command(self, command):
        pass

    def stop(self):
        pass


class Host(Component):
    def __init__(self, project_name, name, label, n_ports, mem, n_disks, filesystem, kernel ):
        """
        :param i: cardinalità dell'Host

        :param name: nome dell'host, per semplicita': 'Host'+i
        :param label:
        :param state: active, l'host è attivo
                      idle, l'host è appena stato creato oppure è stato chiuso per errore, non è attivo
        :param fs: filesystem
        :param kernel: kernel linux per UML
        :param console: comando console_host.name che permette la comunicazione dell'host tramite uml_mconsole
        :param n_ports: numero di porte
        :param mem: memoria
        :param n_disk: numero di dischi da montare sull'host
        :param disks: stringa di comando per l'aggiunta di dischi (con n_disk=1 aggiunge il solo disco root)

        """
        super().__init__()
        self.project = project_name
        self.name = name
        self.label = label
        self.state = 'idle'
        self.fs = filesystem
        self.kernel = kernel
        self.console = self.name + 'cmd'
        self.n_ports = n_ports
        self.mem = mem
        self.n_disks = n_disks
        self.disks = [n_disks]

        self.configuration = str(self.kernel) + ' mem=' + str(self.mem) + 'm '
        for i in range(n_disks-1):
            self.disks[i] = self.project + '_' + self.name + '_disk' + str(i)
            self.configuration = self.configuration + 'ubd' + str(i) + '=/tmp/' + self.disks[i] + '.cow,' + str(self.fs) + ' '
        self.configuration = self.configuration + 'umid=' + self.console

    def run(self, save_path):
        self.state = 'active'
        os.system("xterm -T " + self.name + " -e \"" + self.configuration + "\"")

    def command(self, command):
        r = os.system("uml_mconsole " + self.console + " " + command)
        return r

    def set_mem(self, mem):
        self.mem = mem

    def set_n_disk(self, n_disk):
        self.n_disk = n_disk


class Switch(Component):
    def __init__(self, name, label, n_ports, is_hub, terminal):
        """
        :param i: cardinalita' dello Switch

        :param name: nome dello Switch
        :param n_ports: numero di porte
        :param ishub: True se funziona da Hub
        :param terminal: False se si vuole nascondere il terminal

        """
        super().__init__()
        self.name = name
        self.label = label
        self.state = "idle"
        self.n_ports = n_ports
        self.is_hub = is_hub
        self.terminal = terminal
        self.console = self.name + 'cmd'

    def run(self, save_path):
        daemon = ''
        hub = ''
        if not self.terminal:
            daemon = '-d '
        if self.is_hub:
            hub = '-x '
        self.state = "active"
        os.system("xterm -T " + self.name + " -e \"vde_switch " + daemon + "-n " + str(self.n_ports) + " " + hub
                  + "-s /tmp/" + self.name + " --mgmt /tmp/" + self.console + ".mgmt\"")

    def command(self, command):
        r = os.system("unixcmd -s /tmp/" + self.console + ".mgmt -f /etc/vde2/vdecmd " + command)
        return r

    def poweroff(self):
        os.system("pgrep -f /tmp/" + self.name + " | xargs kill -TERM")

    def set_n_ports(self, n):
        self.n_ports = n

    def set_ishub(self, b):
        self.ishub = b

    def set_terminal(self, b):
        self.terminal = b


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
        if type(A) == type(B):
            self.type = 'cross'
        else:
            if type(A) != Host:
                self.A = B
                self.B = A
        self.name = self.type + '_' + name
        self.port_A = port_A
        self.port_B = port_B

    def make_switch_connection(self):
        os.system("dpipe vde_plug /tmp/" + self.A.name + " = vde_plug /tmp/" + self.B.name)


class Network:

    def __init__(self, name):
        self.name = name
        self.save_path = SAVE_PATH + '/' + name
        self.hosts = []
        self.switches = []
        self.cables = []

    def create_project_path(self):
        if os.path.exists(self.save_path):
            if input("il progetto " + self.name + " esiste gia', sovrascrivere?") == 'no':
                self.name = input("allora inserire altro nome.. ")
                self.save_path = SAVE_PATH + '/' + self.name
            else:
                exit(1)
        os.makedirs(self.save_path)

    def get_save_path(self):
        return self.save_path

    def add_host(self, host):
        self.hosts.append(host)

    def add_switch(self, switch):
        self.switches.append(switch)

    def add_cable(self, cable):
        self.cables.append(cable)

    @staticmethod
    def command_component(command, component):
        r = component.command(command)
        return r

    def start(self):
        """
            avvio Hosts

            avvio Switches

            collego i vari componenti scorrendo la lista cables,
            per ogni cable collego la porta port_A dell'elemento A(sempre Host se cavo straight)
            con la porta port_B dell'elemento B(sempre Switch se cavo straight)

            attivo le altre porte degli host che non sono state collegate a nessun device
            ma che l'utente ha indicato nell'iniziazione dell'host

        """

        for t, h in enumerate(self.hosts):
            t = threading.Thread(target=h.run, args=(self.save_path,))
            t.daemon = True
            t.start()
            print('parte ' + h.name)

        for s in self.switches:
            t = threading.Thread(target=s.run, args=(self.save_path,))
            t.daemon = True
            t.start()
            print('parte ' + s.name)

        time.sleep(0.5)
        for c in self.cables:
            if c.type == 'straight':
                self.command_component(
                    'config eth' + str(c.port_A) + '=vde,/tmp/' + c.B.name + ',,' + str(c.port_B), c.A)
            else:
                if type(c.A) == Host:
                    print('non è possibile collegare due host direttamente, mettici uno switch in mezzo :-)')
                    # self.command_host('config eth' + str(c.port_A) + '=' + c.B.console + ',,' + str(c.port_B), c.A)
                else:
                    t = threading.Thread(target=c.make_switch_connection, args=())
                    t.daemon = True
                    t.start()

            print('collego ' + c.A.name + ' con ' + c.B.name)

        for h in self.hosts:
            print('attivo porte di ' + h.name)
            for p in range(h.n_ports):
                self.command_component('config eth' + str(p) + '=mcast,,,,0', h)

    def shutdown(self):
        for h in self.hosts:
            print('spengo ' + h.name)
            self.command_component('cad', h)

        for s in self.switches:
            print('spengo ' + s.name)
            self.command_component('shutdown', s)
            time.sleep(0.3)

    def poweroff(self):
        for h in self.hosts:
            self.command_component('halt', h)

        for s in self.switches:
            s.poweroff()

    def check_all(self):
        while True:
            time.sleep(0.5)
            for h in self.hosts:
                previous_state = h.state
                if self.command_component('version >/dev/null 2>&1', h) != 0:
                    if previous_state.__eq__('active'):
                        print('(host) ' + h.name + ' chiuso')
                        h.state = 'idle'
                else:
                    h.state = 'active'
            time.sleep(0.5)
            for s in self.switches:
                previous_state = s.state
                # 65280 è il codice di successo di showinfo
                if self.command_component('showinfo >/dev/null 2>&1', s) != 65280:
                    if previous_state.__eq__('active'):
                        print('(switch) ' + s.name + ' chiuso')
                        s.state = 'idle'
                else:
                    s.state = 'active'

    def check_all_thread(self):
        t = threading.Thread(target=self.check_all, args=())
        t.daemon = True
        t.start()
        return

    def save(self):

        list_host = []
        list_switch = []
        list_cable = []

        for h in self.hosts:
            h_dict = {'name': h.name,
                      'label': h.label,
                      'fs': h.fs,
                      'kernel': h.kernel,
                      'n_ports': h.n_ports,
                      'mem': h.mem,
                      'n_disks': h.n_disks}
            list_host.append(h_dict)

        for s in self.switches:
            s_dict = {'name': s.name,
                      'label': s.label,
                      'n_ports': s.n_ports,
                      'is_hub,': s.is_hub,
                      'terminal': s.terminal}
            list_switch.append(s_dict)

        for c in self.cables:
            c_dict = {'name': c.name,
                      'A': c.A.name,
                      'port_A': c.port_A,
                      'B': c.B.name,
                      'port_B': c.port_B}
            list_cable.append(c_dict)

        network_dict = {'network_name': self.name,
                        'host_list': list_host,
                        'switch_list': list_switch,
                        'cable_list': list_cable}

        f_name = self.name + '.json'
        with open(f_name, 'w') as  f:
            json.dump(network_dict, f, indent=3)
        f.close()

        os.system('mv ' + f_name + ' /tmp/')

        os.system('tar -cSzvf ' + self.save_path + '/arc_' + self.name + '_SimNet.tgz -P /tmp/'
                  + self.name + '*.cow /tmp/' + f_name + ' --atime-preserve')

    # def load(self, path):



















