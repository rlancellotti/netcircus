import classes as cl
import os
import time
import string

PATH = os.path.expanduser('~/.netcircus')
RESOURCE_PATH = os.path.expanduser('~/.netcircus/Resources')
SAVE_PATH = os.path.expanduser('~/.netcircus/Projects')


def check_string(s):
    invalid_chars = set(string.punctuation.replace("_", ""))
    if any(char in invalid_chars for char in s):
        return False
    else:
        return True


def main():

    if not os.path.exists(PATH):
        os.makedirs(PATH)
        os.makedirs(SAVE_PATH)
        os.makedirs(RESOURCE_PATH)
    else:
        if not os.path.exists(SAVE_PATH):
            os.makedirs(SAVE_PATH)
        if not os.path.exists(RESOURCE_PATH):
            os.makedirs(RESOURCE_PATH)

    if not os.path.exists(RESOURCE_PATH + '/rootfs.ext4'):
        print('è necessario scaricare un filesystem funzionante')
        return

    if not os.path.exists(RESOURCE_PATH + '/linux'):
        print('è necessario scaricare un kernel funzionante')
        return

    #cl.load(SProjects_PATH + '/eheh/arc_eheh_SimNet.tgz')

    net_name = input('dai un nome al progetto ')

    if not check_string(net_name):
        print(net_name + ' Invalid name project')
        return 1

    net_path = SAVE_PATH + '/' + net_name

    network = cl.Network(net_name)

    host1 = cl.Host(net_name, 'host1', '', 4, 128, 1)
    host2 = cl.Host(net_name, 'host2', '', 2, 128, 1)
    host3 = cl.Host(net_name, 'host3', '', 3, 128, 1)
    switch1 = cl.Switch('switch1', '', 4, False, True)
    switch2 = cl.Switch('switch2', '', 4, False, True)
    network.add_host(host1)
    network.add_host(host2)
    network.add_host(host3)
    network.add_switch(switch1)
    network.add_switch(switch2)
    cable1 = cl.Cable('cable1', switch1, 1, host1, 2)
    cable3 = cl.Cable('cable3', switch1, 2, host2, 2)
    cable2 = cl.Cable('cable2', host3, 1, switch2, 1)
    cable4 = cl.Cable('cable4', switch1, 3, switch2, 2)
    network.add_cable(cable1)
    network.add_cable(cable2)
    network.add_cable(cable3)
    network.add_cable(cable4)

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

    controll = cl.Controller(network)
    network.start_up()

    if not controll.check_start():
        network.shutdown()
        print('errore in avvio, riprovare')
        return 1

    controll.start()

    """
    if input('interrompere? ') == 'si':
        network.shutdown()

    if input('ripartire? ') == 'si':
        network.start()
    """

    if input('spengere il network in modo pulito?\n ') == 'si':
        # if input('vuoi salvare? ') == 'si':
            # cl.save(network, net_path, True)

        controll.set_active(False)
        time.sleep(1)
        network.shutdown()
    else:
        controll.set_active(False)
        time.sleep(1)
        network.poweroff()

    return


main()
