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
import switch

#move to netcircus/tests and run "python3 -m test_host"  


def server():
    server_thread = threading.Thread(target=api.app.run, kwargs={'port': 8080})
    server_thread.start()

class SwitchesTestCase(unittest.TestCase):
    #tests only the backend
    def test_switch_backend_creation1(self):
        net=network.Network()
        data={'id' : 'Switch0' ,'x': 20, 'y': 30, 'width': 48, 'height': 48}
        s=switch.Switch(net, data)
        
        self.assertEqual(20,s.x,'Switch.x not set properly')
        self.assertEqual(30,s.y,'Switch.y not set properly')
        self.assertEqual(48,s.width,'Switch.width not set properly')
        self.assertEqual(48,s.height,'Switch.height not set properly')
        self.assertEqual('Switch0',s.id,'Switch.id not set properly')

    #tests only the backend
    def test_switch_backend_creation2(self):
        net=network.Network()
        data={'id' : 'Switch0' ,'x': 20, 'y': 30, 'width': 48, 'height': 48, 'label' : 'test' , 
              'name' : 'test_name' , 'n_ports':5 , 'is_hub' : True , 'terminal' : True}
              
        s=switch.Switch(net, data)

        self.assertEqual(20,s.x,'Switch.x not set properly')
        self.assertEqual(30,s.y,'Switch.y not set properly')
        self.assertEqual(48,s.width,'Switch.width not set properly')
        self.assertEqual(48,s.height,'Switch.height not set properly')
        self.assertEqual('Switch0',s.id,'Switch.id not set properly')
        self.assertEqual('test',s.label,'Switch.label not set properly')
        self.assertEqual('test_name',s.name,'Switch.name not set properly')
        self.assertEqual(5,s.n_ports,'Switch.n_ports not set properly')
        self.assertEqual(True,s.is_hub,'Switch.is_hub not set properly')
        self.assertEqual(True,s.terminal,'Switch.terminal not set properly')
        
        
    #tests only the frontend
    def test_switch_gui_creation1(self):
        network_model=nc_component.NetworkModel()
        network_model.add_component(nc_component.ComponentModel.TYPE_SWITCH,20,30,48,48)
        switch_id=f'{nc_component.ComponentModel.TYPE_SWITCH}{nc_component.ComponentModel.next_id-1}'
        switch=network_model.components[switch_id]

        self.assertEqual(20,switch.x,'Switch.x not set properly')
        self.assertEqual(30,switch.y,'Switch.y not set properly')
        self.assertEqual(48,switch.width,'Switch.width not set properly')
        self.assertEqual(48,switch.height,'Switch.height not set properly')

    #tests only the frontend
    def test_switch_gui_creation2(self):
        network_model=nc_component.NetworkModel()
        network_model.add_component(nc_component.ComponentModel.TYPE_SWITCH,20,30,48,48)
        switch_id=f'{nc_component.ComponentModel.TYPE_SWITCH}{nc_component.ComponentModel.next_id-1}'
        switch=network_model.components[switch_id]
        update_data={'id': 'Switch0', 'name': 'unnamed', 'label': '',  'n_ports':5 , 'is_hub' : True ,
                      'terminal' : True, 'x': 20, 'y': 30, 'width': 48, 'height': 48}
        switch.update_backend_data(update_data)

        for key in update_data.keys():
            self.assertEqual(update_data[key],switch.backend_data[key], f'Switch.{key} not set properly')

    #tests both backend and frontend
    def test_switch_integration1(self):
        network_model=nc_component.NetworkModel()
        network_model.add_component(nc_component.ComponentModel.TYPE_SWITCH,20,30,48,48)
        switch_id=f'{nc_component.ComponentModel.TYPE_SWITCH}{nc_component.ComponentModel.next_id-1}'
        switch=network_model.components[switch_id]                  #frontend reference
        s=api.net.get_element_by_id(str(switch_id))               #backend reference
        
        
        self.assertEqual(20,s.x, f'Switch.x not set properly')
        self.assertEqual(30,s.y, f'Switch.y not set properly')
        self.assertEqual(48,s.width , f'Switch.width not set properly')
        self.assertEqual(48,s.height, f'Switch.height not set properly')
        

    #tests both backend and frontend (update too)
    def test_switch_integration2(self):
        network_model=nc_component.NetworkModel()
        network_model.add_component(nc_component.ComponentModel.TYPE_SWITCH,25,35,55,46)
        switch_id=f'{nc_component.ComponentModel.TYPE_SWITCH}{nc_component.ComponentModel.next_id-1}'
        switch=network_model.components[switch_id]                  #frontend reference
        update_data={'id': str(switch_id), 'name': 'test_name', 
                      'label': '',  'n_ports':5 , 'is_hub' : True ,'terminal' : True,
                        'x': 50, 'y': 30, 'width': 47, 'height': 28}
        switch.update_backend_data(update_data, True)             
        s=api.net.get_element_by_id(str(switch_id))               #backend reference
        
        for key in update_data.keys():
            self.assertEqual(switch.backend_data[key],getattr(s, key), f'Switch.{key} not set properly')
            self.assertEqual(update_data[key],getattr(s, key), f'Switch.{key} not set properly')

        
    
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
    





