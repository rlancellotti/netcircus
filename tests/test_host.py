import os
import sys
import threading
import time
import unittest
import psutil

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,os.path.join(dir_path, "../backend"))
sys.path.insert(0,os.path.join(dir_path, "../gui"))
import nc_component
import host
import network 
import api

#move to netcircus/tests and run "python3 -m test_host"  


def server():
    server_thread = threading.Thread(target=api.app.run, kwargs={'port': 8080})
    server_thread.start()

class HostsTestCase(unittest.TestCase):
    #tests only the backend
    def test_host_backend_creation1(self):
        net=network.Network()
        data={'id' : 'Host0' ,'x': 20, 'y': 30, 'width': 48, 'height': 48}
        h=host.Host(net, data)
        
        self.assertEqual(20,h.x,'Host.x not set properly')
        self.assertEqual(30,h.y,'Host.y not set properly')
        self.assertEqual(48,h.width,'Host.width not set properly')
        self.assertEqual(48,h.height,'Host.height not set properly')
        self.assertEqual('Host0',h.id,'Host.id not set properly')

    #tests only the backend
    def test_host_backend_creation2(self):
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
        
    #tests only the frontend
    def test_host_gui_creation1(self):
        network_model=nc_component.NetworkModel()
        network_model.add_component(nc_component.ComponentModel.TYPE_HOST,20,30,48,48)
        host_id=f'{nc_component.ComponentModel.TYPE_HOST}{nc_component.ComponentModel.next_id-1}'
        host=network_model.components[host_id]

        self.assertEqual(20,host.x,'Host.x not set properly')
        self.assertEqual(30,host.y,'Host.y not set properly')
        self.assertEqual(48,host.width,'Host.width not set properly')
        self.assertEqual(48,host.height,'Host.height not set properly')

    #tests only the frontend
    def test_host_gui_creation2(self):
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

    #tests both backend and frontend
    def test_host_integration1(self):
        network_model=nc_component.NetworkModel()
        network_model.add_component(nc_component.ComponentModel.TYPE_HOST,20,30,48,48)
        host_id=f'{nc_component.ComponentModel.TYPE_HOST}{nc_component.ComponentModel.next_id-1}'
        host=network_model.components[host_id]                  #frontend reference
        h=api.net.get_element_by_id(str(host_id))               #backend reference
        
        
        self.assertEqual(20,h.x, f'Host.x not set properly')
        self.assertEqual(30,h.y, f'Host.y not set properly')
        self.assertEqual(48,h.width , f'Host.width not set properly')
        self.assertEqual(48,h.height, f'Host.height not set properly')
        

    #tests both backend and frontend (update too)
    def test_host_integration2(self):
        network_model=nc_component.NetworkModel()
        network_model.add_component(nc_component.ComponentModel.TYPE_HOST,25,35,55,46)
        host_id=f'{nc_component.ComponentModel.TYPE_HOST}{nc_component.ComponentModel.next_id-1}'
        host=network_model.components[host_id]                  #frontend reference
        update_data={'id': str(host_id), 'name': 'test_name', 'description': 'descr', 'kernel': 'custom/path', 
                        'filesystem': '/path/Documenti/Code/NetCircus/image/root.ext4', 
                        'cow': '/path/Documenti/Code/NetCircus/work/Host0.cow', 'mem': '76',
                        'x': 50, 'y': 30, 'width': 47, 'height': 28}
        host.update_backend_data(update_data, True)             
        h=api.net.get_element_by_id(str(host_id))               #backend reference
        
        for key1 in update_data.keys():
            key2=key1
            if key1=='filesystem':
                key2='fs'
            if key1=='name':
                continue
            self.assertEqual(host.backend_data[key1],getattr(h, key2), f'Host.{key1} not set properly')
            self.assertEqual(update_data[key1],getattr(h, key2), f'Host.{key1} not set properly')

        
    
if __name__ == '__main__':
    server()                                #starting server in a new thread
    time.sleep(2)  
    unittest.main(exit=False)               #testing
    
    
    port = 8080
    for proc in psutil.net_connections():
        if proc.laddr.port == port and proc.status == 'LISTEN':
            pid = proc.pid
            break
    
    process = psutil.Process(pid)
    process.terminate()                     #killin the server process
    





