import os
import time
import string
from . import netcircus_paths
from .host import Host
from .switch import Switch
from .network import Network
from .cable import Cable

def check_string(s):
    invalid_chars = set(string.punctuation.replace("_", ""))
    if any(char in invalid_chars for char in s):
        return False
    else:
        return True


def check_paths():
    for p in [netcircus_paths.PATH, netcircus_paths.SAVE_PATH, netcircus_paths.FS_PATH, netcircus_paths.KERNEL_PATH]:
        if not os.path.exists(p):
            os.makedirs(p)

def simple_main():
    network = Network('test_network')
    host1 = Host(network, data={'id': 'host1', 'name':'host1', 'mem': 96})
    host2 = Host(network, data={'id': 'host2', 'name':'host2', 'mem': 96})
    switch1 = Switch(network, data={'id':'switch1', 'terminal': True})
    Cable(network, 'cable1', 'cable1', host1, 0, switch1, 1)
    Cable(network, 'cable2', 'cable1', host2, 0, switch1, 2)

    network.start_up()
    #print('Network is up')
    #print('End of ctrl()')
    time.sleep(30)
    #print(json.dumps(network.dump(), indent=2))
    #time.sleep(1)
    network.shutdown()
    # FIXME: must wait for proper sutdown before saving.
    time.sleep(10)
    #print('saving network')
    network.save()

def restore():
    print('restoring network')
    n2=Network(tar_name=f'{netcircus_paths.SAVE_PATH}/test.tgz')
    n2.start_up()
    time.sleep(20)
    n2.shutdown()
 
if __name__ == '__main__':
    check_paths()
    simple_main()
    #restore()
