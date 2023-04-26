import netcircus_paths
import os
import logging 
import threading
import time

class Component:
    Status_Running=1
    Status_Starting=2
    Status_Stopped=0
    Status_Names={1: 'RUNNING', 2: 'STARTING', 0: 'STOPPED'}
    check_interval=1

    def __init__(self, id):
        logging.basicConfig(filename='test.log', level=logging.DEBUG)
        self.logger=logging.getLogger(id)
        self.status=Component.Status_Stopped
        self.name = id
        self.description = None
        self.console = None
        self.console_signals = {'stop': None,
                                'halt': None,
                                'check': None}
        #self.start_check()

    def get_cmdline(self) -> str:
        return ''

    def start_check(self):
        self.log(logging.DEBUG, 'call to start_check')
        self.controller=threading.Thread(target=self.run_check, daemon=True)
        self.controller.start()

    def run_check(self):
        while self.status!=Component.Status_Stopped:
            time.sleep(self.check_interval)
            self.check()

    def dump(self):
        pass

    def clean(self):
        pass

    def log(self, loglevel, msg, *args):
        self.logger.log(loglevel, msg, *args)

    def launch(self):
        print(f'starting with component with {self.get_cmdline()}')
        os.system(f'x-terminal-emulator -T {self.name} -e \"{self.get_cmdline()}\"')
        self.status=Component.Status_Starting
        self.log(logging.INFO, 'Starting')
        self.start_check()

    def command(self, command):
        pass

    def update_status(self, check_rv):
        if check_rv==True:
            if self.status!=Component.Status_Running:
                self.log(logging.INFO, 'status change %s to %s', Component.Status_Names[self.status], Component.Status_Names[Component.Status_Running])
            self.status=Component.Status_Running
        if check_rv==False:
            if self.status!=Component.Status_Stopped:
                self.log(logging.INFO, 'status change %s to %s', Component.Status_Names[self.status], Component.Status_Names[Component.Status_Stopped])
            self.status=Component.Status_Stopped

    def check(self):
        rv=None
        self.log(logging.DEBUG, 'call to check()')
        if self.console_signals['check'] is not None:
            rv = self.command(self.console_signals['check'])
            self.update_status(rv)
        return rv

    def shutdown(self):
        self.command(self.console_signals['stop'])
        self.log(logging.INFO, 'Shutting down')
        self.stop()

    def halt(self):
        self.command(self.console_signals['halt'])
        self.log(logging.INFO, 'Halting')
        self.stop()
    
    def stop(self):
        pass
