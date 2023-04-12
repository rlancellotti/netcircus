import netcircus_paths
import component
import os

class Switch(component.Component):
    def __init__(self, network, name=None, label=None, n_ports=None, is_hub=False, terminal=True, dump=None):
        """

        :param n_ports: numero di porte
        :param ishub: True se funziona da Hub
        :param terminal: False se si vuole nascondere il terminal

        """
        super().__init__()
        if dump is None:
            self.init_from_parameters(name, label, n_ports, is_hub, terminal)
        else:
            self.init_from_dump(dump)
        self.console = self.name + '_cmd'
        self.console_signals['stop'] = 'shutdown'
        self.console_signals['halt'] = 'shutdown'
        self.console_signals['check'] = 'showlist > /dev/null 2>&1'
        daemon = '' if self.terminal else '-daemon'
        hub = '-hub' if self.is_hub else ''
        #FIXME: use correct paths
        self.cmdline = f"vde_switch {daemon} -n {str(self.n_ports)} {hub} -s {netcircus_paths.WORKAREA}/{self.name} --mgmt {netcircus_paths.WORKAREA}/{self.console}.mgmt"
        print(self.cmdline)
        network.add(self)

    def init_from_parameters(self, name, label, n_ports, is_hub, terminal):
        self.name = name
        self.label = label
        self.n_ports = n_ports
        self.is_hub = is_hub
        self.terminal = terminal
    
    def init_from_dump(self, dump):
        self.name = dump['name']
        self.label = dump['label']
        self.n_ports = dump['n_ports']
        self.is_hub = dump['is_hub']
        self.terminal = dump['terminal']

    def dump(self) -> dict:
        rv={}
        rv['name'] = self.name
        rv['label'] = self.label
        rv['n_ports'] = self.n_ports
        rv['is_hub'] = self.is_hub
        rv['terminal'] = self.terminal
        return rv

    def command(self, command):
        # 65280 exit status comando unixcmd
        if os.system(f'unixcmd -s {netcircus_paths.WORKAREA}/{self.console}.mgmt -f /etc/vde2/vdecmd {command}') == 65280:
            return True
        return False

    def halt(self):
        os.system(f'pgrep -f {netcircus_paths.WORKAREA}/self.name | xargs kill -TERM')

    def check(self):
        return os.path.exists(f'{netcircus_paths.WORKAREA}/{self.console}.mgmt')
