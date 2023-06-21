import os
import sys
import unittest
import host
import network 

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,os.path.join(dir_path, "../../gui"))
import nc_component

#move to netcircus/backend and run "python3 -m unit_tests.test_host"  or  "python3 -m unittest discover unit_tests"
#remember to start the backend before, otherwise gui tests won't work 

class HostsTestCase(unittest.TestCase):
    def test_backend_creation1(self):
        net=network.Network()
        data={'id' : 'Host0' ,'x': 20, 'y': 30, 'width': 48, 'height': 48}
        h=host.Host(net, data)
        
        self.assertEqual(20,h.x,'Host.x not set properly')
        self.assertEqual(30,h.y,'Host.y not set properly')
        self.assertEqual(48,h.width,'Host.width not set properly')
        self.assertEqual(48,h.height,'Host.height not set properly')
        self.assertEqual('Host0',h.id,'Host.id not set properly')

    def test_backend_creation2(self):
        net=network.Network()
        data={'id' : 'Host0' ,'x': 20, 'y': 30, 'width': 48, 'height': 48, 'description' : 'test' , 
              'kernel' : 'kenrel_test' , 'name' : 'test_name' , 'filesystem' : 'file' , 
              'cow' : 'cowfile' , 'mem' : 90} 
        h=host.Host(net, data)

        self.assertEqual(20,h.x,'Host.x not set properly')
        self.assertEqual(30,h.y,'Host.y not set properly')
        self.assertEqual(48,h.width,'Host.width not set properly')
        self.assertEqual(48,h.height,'Host.height not set properly')
        self.assertEqual('Host0',h.id,'Host.id not set properly')
        self.assertEqual('test',h.description,'Host.description not set properly')
        self.assertEqual('kenrel_test',h.kernel,'Host.kernel not set properly')
        self.assertEqual('test_name',h.name,'Host.name not set properly')
        self.assertEqual('file',h.fs,'Host.fs not set properly')
        self.assertEqual('cowfile',h.cow,'Host.cow not set properly')
        self.assertEqual(90,h.mem,'Host.mem not set properly')
        
    def test_gui_creation1(self):
        network_model=nc_component.NetworkModel()
        network_model.add_component(nc_component.ComponentModel.TYPE_HOST,20,30,48,48)
        host_id=f'{nc_component.ComponentModel.TYPE_HOST}{nc_component.ComponentModel.next_id-1}'
        host=network_model.components[host_id]

        self.assertEqual(20,host.x,'Host.x not set properly')
        self.assertEqual(30,host.y,'Host.y not set properly')
        self.assertEqual(48,host.width,'Host.width not set properly')
        self.assertEqual(48,host.height,'Host.height not set properly')

    def test_gui_creation2(self):
        network_model=nc_component.NetworkModel()
        network_model.add_component(nc_component.ComponentModel.TYPE_HOST,20,30,48,48)
        host_id=f'{nc_component.ComponentModel.TYPE_HOST}{nc_component.ComponentModel.next_id-1}'
        host=network_model.components[host_id]
        update_data={'id': 'Host0', 'name': 'unnamed', 'description': '', 'kernel': '/usr/bin/linux', 
                        'filesystem': '/path/Documenti/Code/NetCircus/image/root.ext4', 
                        'cow': '/path/Documenti/Code/NetCircus/work/Host0.cow', 'mem': '96',
                        'x': 20, 'y': 30, 'width': 48, 'height': 48}
        host.update_backend_data(update_data)

        for key in update_data.keys():
            self.assertEqual(update_data[key],host.backend_data[key], f'Host.{key} not set properly')
        
        
if __name__ == '__main__':
	unittest.main()





