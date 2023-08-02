import time
import os
import sys
import unittest
import json

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,os.path.join(dir_path, "../backend"))
import api


#move to netcircus/tests and run "python3 -m test_api_requests"  

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.app = api.app.test_client()

    def test_get_kernels(self):
        response = self.app.get('/api/v1/system/kernels')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_get_filesystems(self):
        response = self.app.get('/api/v1/system/filesystems')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertGreater(len(data), 0)

    def test_get_networkname(self):
        response = self.app.get('/api/v1/system/networkname')
        self.assertEqual(response.status_code, 200)
    
    def test_post_kernels(self):
        response = self.app.post('/api/v1/system/kernels', json={})
        self.assertEqual(response.status_code, 405)

    def test_post_filesystems(self):
        response = self.app.post('/api/v1/system/filesystems', json={})
        self.assertEqual(response.status_code, 405)

    def test_post_networkname(self):
        response = self.app.post('/api/v1/system/networkname', json={'name':'test'})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data,'test' ,'Networkname not set properly')

    def test_host_basic(self):
        response = self.app.post('/api/v1/host/Host0', json={'x': 10, 'y': 20, 'width': 48, 'height': 48})
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['x'],10 ,'Host.x not set properly')
        self.assertEqual(data['y'],20 ,'Host.y not set properly')
        self.assertEqual(data['width'],48 ,'Host.width not set properly')
        self.assertEqual(data['height'],48 ,'Host.height not set properly')
        self.assertGreater(len(data), 0)

    def test_get_host(self):
        self.app.post('/api/v1/host/Host0', json={'name':'test_name1' ,'x': 10, 'y': 20, 'width': 48, 'height': 48})
        response = self.app.get('/api/v1/host/Host0')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'],'Host0' ,'Can not get host properly')


    def test_delete_host(self):
        self.app.post('/api/v1/host/Host0', json={'name':'test_name1' ,'x': 10, 'y': 20, 'width': 48, 'height': 48})
        response = self.app.delete('/api/v1/host/Host0')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data,None,'Can not delete host properly')

    def test_switch_basic(self):
        response = self.app.post('/api/v1/switch/Switch0', json={'x': 10, 'y': 20, 'width': 48, 'height': 48})
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertEqual(data['x'],10 ,'Switch.x not set properly')
        self.assertEqual(data['y'],20 ,'Switch.y not set properly')
        self.assertEqual(data['width'],48 ,'Switch.width not set properly')
        self.assertEqual(data['height'],48 ,'Switch.height not set properly')
        self.assertGreater(len(data), 0)

    def test_get_switch(self):
        self.app.post('/api/v1/switch/Switch0', json={'name':'test_name1' ,'x': 10, 'y': 20, 'width': 48, 'height': 48})
        response = self.app.get('/api/v1/switch/Switch0')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['id'],'Switch0' ,'Can not get switch properly')

    def test_delete_switch(self):
        self.app.post('/api/v1/switch/Switch0', json={'name':'test_name1' ,'x': 10, 'y': 20, 'width': 48, 'height': 48})
        response = self.app.delete('/api/v1/switch/Switch0')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data,None,'Can not delete switch properly')        

    def test_non_existing_route(self):
        response = self.app.get('/api/v1/nonexistingroute')
        self.assertEqual(response.status_code, 404)

    def test_get_host_list(self):
        self.app.post('/api/v1/host/Host0', json={'name':'test_name1' ,'x': 10, 'y': 20, 'width': 48, 'height': 48})
        self.app.post('/api/v1/host/Host1', json={'name':'test_name2' ,'x': 10, 'y': 20, 'width': 48, 'height': 48})
        response = self.app.get('/api/v1/host')
        
        data = json.loads(response.data)
        self.assertEqual(data,['test_name1','test_name2'] ,'Host_list not set properly')


    def test_clean(self):
        response=self.app.post('/api/v1/action/clean', json={})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data,None,'Can not clean properly')
        
    def test_start(self):
        return          #this test actually start an host, comment the return in order to test
        response=self.app.post('/api/v1/action/start', json={})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data,None,'Can not start properly')

    def test_stop(self):
        response=self.app.post('/api/v1/action/stop', json={})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data,None,'Can not stop properly')

    def test_halt(self):
        response=self.app.post('/api/v1/action/halt', json={})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data,None,'Can not halt properly')

    def test_save(self):
        return
        self.app.post('/api/v1/action/clean', json={})              #cleaning before testing
        self.app.post('/api/v1/host/Host0', json={'name':'test_name1' ,'x': 10, 'y': 20, 'width': 48, 'height': 48})  #add Host0

        #FIXME  #!!!!Host need to start in order to have the cow file, otherwise save would fail
        self.app.post('/api/v1/action/start', json={})             #start Host0
        time.sleep(20)
        response=self.app.post('/api/v1/action/save', json={})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data,None,'Can not save properly')

if __name__ == '__main__':
    unittest.main()
    
