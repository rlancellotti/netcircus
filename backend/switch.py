import netcircus_paths
from component import Component
import logging
import os

class Switch(Component):
    def __init__(self, network, data):
        """

        :param n_ports: numero di porte
        :param ishub: True se funziona da Hub
        :param terminal: False se si vuole nascondere il terminal

        """
        super().__init__(data['id'])
        self.network=network
        self.id=data['id'] 
        self.name = data['name'] if 'name' in data.keys() else 'unnamed'
        self.label = data['label'] if 'label' in data.keys() else ''
        self.x = data['x' ] if 'x' in data.keys() else '0.0'
        self.y = data['y' ] if 'y' in data.keys() else '0.0'
        self.width = data['width' ] if 'width' in data.keys() else '0.0'
        self.height = data['height' ] if 'height' in data.keys() else '0.0'
        self.n_ports=data['n_ports' ] if 'n_ports' in data.keys() else 4
        self.is_hub = data['is_hub'] if 'is_hub' in data.keys() else False
        self.terminal = data['terminal'] if 'terminal' in data.keys() else False
        self.ready=False
        self.console = self.id + '_cmd'
        self.console_signals['stop'] = 'shutdown'
        self.console_signals['halt'] = 'shutdown'
        self.console_signals['check'] = 'showlist > /dev/null 2>&1'

        
        #FIXME: use correct paths
        network.add(self)

    def get_cmdline(self) -> str:
        daemon = '' if self.terminal else '-daemon'
        hub = '-hub' if self.is_hub else ''
        cmdline=f"vde_switch {daemon} -n {int(self.n_ports)} {hub} -s {netcircus_paths.WORKAREA}/{self.id} --mgmt {netcircus_paths.WORKAREA}/{self.console}.mgmt"
        return cmdline

    def init_from_parameters(self, name, label, n_ports, is_hub, terminal):
        self.name = name
        self.label = label
        self.n_ports = n_ports
        self.is_hub = is_hub
        self.terminal = terminal
    
    def init_from_dump(self, dump):
        self.name = dump['name'] if 'name' in dump.keys() else 'unnamed'
        self.label = dump['label'] if 'label' in dump.keys() else 'no_label'
        self.n_ports = dump['n_ports'] if 'n_ports' in dump.keys() else 4
        self.is_hub = dump['is_hub'] if 'is_hub' in dump.keys() else False
        self.terminal = dump['terminal'] if 'terminal' in dump.keys() else False

    def dump(self) -> dict:
        rv={}
        rv['id']=self.id
        rv['name'] = self.name
        rv['label'] = self.label
        rv['n_ports'] = self.n_ports
        rv['is_hub'] = self.is_hub
        rv['terminal'] = self.terminal
        rv['x']=self.x
        rv['y']=self.y
        rv['width']=self.width
        rv['height']=self.height
        return rv

    def command(self, command):
        # 65280 exit status comando unixcmd
        if os.system(f'unixcmd -s {netcircus_paths.WORKAREA}/{self.console}.mgmt -f /etc/vde2/vdecmd {command}') == 65280:
            return True
        return False

    def halt(self):
        os.system(f'pgrep -f {netcircus_paths.WORKAREA}/{self.id} | xargs kill -TERM')

    def check(self):
        return os.path.exists(f'{netcircus_paths.WORKAREA}/{self.console}.mgmt')

    def update(self, data):
            if 'name' in data.keys(): self.name=data['name']
            if 'label' in data.keys(): self.label=data['label']
            if 'n_ports' in data.keys(): self.n_ports=data['n_ports']
            if 'is_hub' in data.keys(): self.is_hub=data['is_hub']
            if 'terminal' in data.keys(): self.terminal=data['terminal']
            if 'x' in data.keys(): self.x=data['x']
            if 'y' in data.keys(): self.y=data['y']
            if 'width' in data.keys(): self.width=data['width']
            if 'height' in data.keys(): self.height=data['height']
            print(self.dump())