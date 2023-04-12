import netcircus_paths
from host import Host
from switch import Switch
from cable import Cable
import os
import threading
import time
import json
import tarfile

class Network:
    def __init__(self, name=None, tar_name=None):
        self.conf_name = f'{netcircus_paths.WORKAREA}/config.json'
        self.name = name
        self.hosts = []
        self.switches = []
        self.cables = []
        if tar_name is not None:
            self.load(tar_name)

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
                print('Shutting down ' + c.name)
                c.shutdown()

    def poweroff(self):
        for c in self.hosts + self.switches:
            if c.check:
                print('Force shutdown for ' + c.name)
                c.halt()


    def dump(self):
        rv = {'network_name': self.name}
        rv['hosts'] = [h.dump() for h in self.hosts]
        rv['switches'] = [s.dump() for s in self.switches]
        rv['cables'] = [c.dump() for c in self.cables]
        return rv
    
    def save(self, tar_name=None):
        if tar_name is None:
            tar_name = f'{netcircus_paths.SAVE_PATH}/{self.name}.tgz'
        with open(self.conf_name, 'w') as f:
            json.dump(self.dump(), f, indent=2)
        with tarfile.open(tar_name, 'w:gz', format=tarfile.GNU_FORMAT) as tar:
            tar.add(self.conf_name, arcname=os.path.basename(self.conf_name))
            for f in [h.cow for h in self.hosts]:
                tar.add(f, arcname=os.path.basename(f), filter=filter_cow)
        # clean files
        os.remove(self.conf_name)
        for f in [h.cow for h in self.hosts]:
            os.remove(f)

    def load_config(self):
        with open(self.conf_name, 'r') as f:
            conf=json.load(f)
            self.name=conf['network_name']
            # hosts
            for h in conf['hosts']:
                self.add(Host(self, dump=h))
            # switches
            for s in conf['switches']:
                self.add(Switch(self, dump=s))
            # cables
            for c in conf['cables']:
                self.add(Cable(self, dump=c))

    def load(self, tar_name):
        with tarfile.open(tar_name, 'r:gz') as tar:
            # restore_config
            tar.extract(os.path.basename(self.conf_name), path=netcircus_paths.WORKAREA)
            for f in tar.getmembers():
                print(get_info(f))
        # load config
        self.load_config()
            

def get_info(f: tarfile.TarInfo) -> str:
    return f'{f.name} {f.size} {typename(f.type)}'

def typename(ftype):
    ftypes={tarfile.REGTYPE: 'REGTYPE', tarfile.AREGTYPE: 'AREGTYPE', 
            tarfile.LNKTYPE: 'LNKTYPE', tarfile.SYMTYPE: 'SYMTYPE', 
            tarfile.DIRTYPE: 'DIRTYPE', tarfile.FIFOTYPE: 'FIFOTYPE', 
            tarfile.CONTTYPE: 'CONTTYPE', tarfile.CHRTYPE: 'CHRTYPE', 
            tarfile.BLKTYPE: 'BLKTYPE', tarfile.GNUTYPE_SPARSE: 'GNUTYPE_SPARSE'}
    return ftypes[ftype]

def filter_cow(f: tarfile.TarInfo) ->tarfile.TarInfo:
    f.type = tarfile.GNUTYPE_SPARSE
    #print(f.name, f.size, typename(f.type))
    return f



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