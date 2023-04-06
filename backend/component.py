import netcircus_paths
import os

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
        self.cmdline = ''

    def launch(self):
        os.system(f'x-terminal-emulator -T {self.name} -e \"{self.cmdline}\"')

    def command(self, command):
        pass

    def check(self):
        r = self.command(self.console_signals['check'])
        return r

    def shutdown(self):
        self.command(self.console_signals['stop'])

    def halt(self):
        self.command(self.console_signals['halt'])
