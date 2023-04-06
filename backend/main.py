import os
import time
import string
import netcircus_paths
from host import Host
from switch import Switch
from network import Network
from cable import Cable
from controller import Controller


def check_string(s):
    invalid_chars = set(string.punctuation.replace("_", ""))
    if any(char in invalid_chars for char in s):
        return False
    else:
        return True


def main():
    # FIXME: stronger check for filesystem existence
    if not os.path.exists(netcircus_paths.PATH):
        os.makedirs(netcircus_paths.PATH)
        os.makedirs(netcircus_paths.SAVE_PATH)
        os.makedirs(netcircus_paths.FS_PATH)
        os.makedirs(netcircus_paths.KERNEL_PATH)

    #cl.load(SProjects_PATH + '/eheh/arc_eheh_SimNet.tgz')

    #net_name = input('dai un nome al progetto ')
    net_name = 'test'

    #if not check_string(net_name):
    #    print(net_name + ' Invalid name project')
    #    return 1

    net_path = netcircus_paths.SAVE_PATH + '/' + net_name

    network = Network(net_name)

    host1 = Host(net_name, 'host1', '', 4, 128, 1)
    host2 = Host(net_name, 'host2', '', 2, 128, 1)
    host3 = Host(net_name, 'host3', '', 3, 128, 1)
    switch1 = Switch('switch1', '', 4, False, True)
    switch2 = Switch('switch2', '', 4, False, True)
    network.add(host1)
    network.add(host2)
    network.add(host3)
    network.add(switch1)
    network.add(switch2)
    cable1 = Cable('cable1', switch1, 1, host1, 2)
    cable3 = Cable('cable3', switch1, 2, host2, 2)
    cable2 = Cable('cable2', host3, 1, switch2, 1)
    cable4 = Cable('cable4', switch1, 3, switch2, 2)
    network.add(cable1)
    network.add(cable2)
    network.add(cable3)
    network.add(cable4)

    print('\nIl network è così composto:\n')

    for h in network.hosts:
        print(h.name)
        if not check_string(h.name):
            print(h.name + ' invalid name')
            return 1

    for s in network.switches:
        print(s.name)
        if not check_string(s.name):
            print(s.name + ' invalid name')
            return 1

    for c in network.cables:
        print(c.name + ": " + c.A.name + ", " + c.B.name)
        if not check_string(c.name):
            print(c.name + ' invalid name')
            return 1

    ctrl = Controller(network)
    network.start_up()

    if not ctrl.check_start():
        network.shutdown()
        print('errore in avvio, riprovare')
        return 1

    ctrl.start()

    if input('interrompere? ') == 'si':
        network.shutdown()

    if input('ripartire? ') == 'si':
        network.start()

    if input('spengere il network in modo pulito?\n ') == 'si':
        # if input('vuoi salvare? ') == 'si':
            # cl.save(network, net_path, True)

        ctrl.set_active(False)
        time.sleep(1)
        network.shutdown()
    else:
        ctrl.set_active(False)
        time.sleep(1)
        network.poweroff()

    return

def simple_main():
    net_name = 'test'
    #net_path = f'{netcircus_paths.SAVE_PATH}/{net_name}'
    network = Network(net_name)
    host1 = Host(net_name, 'host1', '', mem=96, ndisks=1)
    host2 = Host(net_name, 'host2', '', mem=96, ndisks=1)
    switch1 = Switch('switch1', '', 4)
    network.add(host1)
    network.add(host2)
    network.add(switch1)
    network.add(Cable('cable1', host1, 0, switch1, 1))
    network.add(Cable('cable2', host2, 0, switch1, 2))

    ctrl = Controller(network)
    network.start_up()
    print('Network is up')
    ctrl.start()
    print('End of ctrl()')
    time.sleep(10)
    #ctrl.set_active(False)
    #time.sleep(1)
    #network.shutdown()
    print('End of main()')


if __name__ == '__main__':
    #main()
    simple_main()
