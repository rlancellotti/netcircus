import netcircus_paths
from host import Host
from switch import Switch
from cable import Cable
import os
import threading
import time
import json
import tarfile
import logging

ELEMENT_HOST = 1 
ELEMENT_SWITCH = 2 
ELEMENT_CABLE = 4

class Network:
    def __init__(self, name='', tar_name=None):
        self.conf_name = f'{netcircus_paths.WORKAREA}/config.json'
        self.name = name
        self.hosts = []
        self.switches = []
        self.cables = []
        self.objects={}
        if tar_name is not None:
            self.load(tar_name)

    def set_name(self, name):
        self.name=name

    def get_name(self):
        return self.name

    def get_elements(self, element_type_mask):
        rv = []
        if element_type_mask & ELEMENT_HOST:
            rv += [e.name for e in self.hosts]
        if element_type_mask & ELEMENT_SWITCH:
            rv += [e.name for e in self.switches]
        if element_type_mask & ELEMENT_CABLE:
            rv += [e.name for e in self.links]
        return rv

    def add(self, obj):
        self.objects[obj.id]=obj
        if type(obj) == Host:
            self.hosts.append(obj)
            return
        if type(obj) == Switch:
            self.switches.append(obj)
            return
        if type(obj) == Cable:
            self.cables.append(obj)
            return

    def get_element_by_id(self, n):
        if n in self.objects.keys():
            return self.objects[n]
        else: return None

    def delete_element(self, id):
        obj = self.get_element_by_id(id)
        if obj is not None:
            del(self.objects[obj.id])
            if type(obj) == Cable:
                self.cables.remove(obj)
            for c in self.cables:
                if c.a == obj or c.b == obj:
                    self.cables.remove(c)
            if type(obj) == Host:
                self.hosts.remove(obj)
                return
            if type(obj) == Switch:
                self.switches.remove(obj)
                return

    def start_up(self):
        print('executing network startup')
        for c in self.hosts + self.switches:
            print(f'network start of {c.id} -> {c.name}')
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
        print('executing network shutdown')
        for c in self.hosts + self.switches:
            if c.check():
                print(f'network stop of {c.id} -> {c.name}')
                c.shutdown()

    def poweroff(self):
        for c in self.hosts + self.switches:
            if c.check:
                #print('Force shutdown for ' + c.name)
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
        # Not working: Sparse file support in libtar is read-only.
        #with tarfile.open(tar_name, 'w:gz', format=tarfile.GNU_FORMAT) as tar:
        #    tar.add(self.conf_name, arcname=os.path.basename(self.conf_name))
        #    for f in [h.cow for h in self.hosts]:
        #        tar.add(f, arcname=os.path.basename(f), filter=filter_cow)
        filenames = [os.path.basename(self.conf_name)] + [os.path.basename(h.cow) for h in self.hosts]

        os.system('cd %s; tar cSzf %s %s' % (netcircus_paths.WORKAREA, tar_name, ' '.join(filenames)))
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
                Host(self, dump=h)
            # switches
            for s in conf['switches']:
                Switch(self, dump=s)
            # cables
            for c in conf['cables']:
                Cable(self, dump=c)

    def load(self, tar_name):
        with tarfile.open(tar_name, 'r:gz') as tar:
            # restore_config
            tar.extract(os.path.basename(self.conf_name), path=netcircus_paths.WORKAREA)
            for f in tar.getmembers():
                if f.name.endswith('.cow'):
                    tar.extract(f, path=netcircus_paths.WORKAREA)
        # load config
        self.load_config()

    def clean(self):
        for c in self.hosts:
            del(self.objects[c.id])
            c.clean()
            self.hosts.remove(c)
        for c in self.switches:
            del(self.objects[c.id])
            c.clean()
            self.switches.remove(c)
        for c in self.cables:
            del(self.objects[c.id])
            self.cables.remove(c)


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
