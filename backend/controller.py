import netcircus_paths
from network import Network
import time
import threading

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
                print(h.name + ' not started correctly')
                return False
            else:
                self.hosts_states[h] = 'opened'
                print(h.name + " started correctly")
        for s in self.net.switches:
            if not s.check():
                print(s.name + ' not started correctly')
                return False
            else:
                self.switches_states[s] = 'opened'
                print(s.name + " started correctly")
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
























