import os
import sys


dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,dir_path)
from flask import Flask, request
from flask_restful import Resource, Api
import netcircus_paths
import network
import host
import switch
import cable

app = Flask(__name__)
api=Api(app)
basePath = '/api/v1'

net=network.Network()

class SystemResource(Resource):
    def get(self, res):
        if res == 'kernels':
            return netcircus_paths.get_kernels(), 200
        if res == 'filesystems':
            return netcircus_paths.get_filesystems(), 200
        if res == 'networkname':
            return net.get_name(), 200
        if res == 'workarea':
            return netcircus_paths.WORKAREA, 200
        return None, 404
    def post(self, res):
        n=request.json
        if res in ['kernels', 'filesystems']:
            return None, 405
        if res == 'networkname':
            # FIXME: must add stronger validation
            if 'name' in n.keys():
                net.set_name(n['name'])
                return net.get_name(), 201
            else: return None, 400
        return None, 404

class HostList(Resource):
    def get(self):
        return net.get_elements(network.ELEMENT_HOST)

class HostResource(Resource):
    def get(self, id):
        h=net.get_element_by_id(id)
        if h is not None:
            return h.dump(), 200
        else: return None, 404
    def post(self, id):
        data=request.json
        data['id']=id
        print(id, data)
        h=net.get_element_by_id(id)
        print(h)
        if h is not None and type(h) is host.Host:
            h.update(data)
        else:
            h=host.Host(net, data)
        return h.dump(), 201
    def delete(self, id):
        if net.get_element_by_id(id) is not None:
            net.delete_element(id)
            return None, 201
        else: return None, 404

class CableResource(Resource):
    def get(self, id):
        c=net.get_element_by_id(id)
        if c is not None:
            return c.dump(), 200
        else: return None, 404
    def post(self, id):
        data=request.json
        data['id']=id
        print(id, data)
        c=cable.Cable(net, id,endpoint_A=net.get_element_by_id(data['endpoint_A']), port_A= data['port_A'],
                      endpoint_B=net.get_element_by_id(data['endpoint_B']), port_B=data['port_B'])
        return c.dump(), 201
    
    def delete(self, id):
        if net.get_element_by_id(id) is not None:
            net.delete_element(id)
            return None, 201
        else: return None, 404

class SwitchResource(Resource):
    def get(self, id):
        s=net.get_element_by_id(id)
        if s is not None:
            return s.dump(), 200
        else: return None, 404
    def post(self, id):
        data=request.json
        data['id']=id
        print(id, data)
        s=net.get_element_by_id(id)
        print(s)
        if s is not None and type(s) is switch.Switch:
            s.update(data)
        else:
            s=switch.Switch(net, data)
        return s.dump(), 201
    def delete(self, id):
        if net.get_element_by_id(id) is not None:
            net.delete_element(id)
            return None, 201
        else: return None, 404

class ActionResource(Resource):
    def post(self, action):
        if action == 'clean':
            net.clean()
            return None, 200
        if action == 'start':
            net.start_up()
            return None, 200
        if action == 'stop':
            net.shutdown()
            return None, 200
        if action == 'halt':
            net.poweroff()
            return None, 200
        if action == 'save':
            # FIXME: can use filename from request body
            data=request.json
            name=data['name']
            net.save(name)
            return None, 200
        if action== 'load':
            data=request.json
            name=data['name']
            net.load(name)

api.add_resource(SystemResource, f'{basePath}/system/<string:res>')
api.add_resource(ActionResource, f'{basePath}/action/<string:action>')
api.add_resource(HostList, f'{basePath}/host')
api.add_resource(HostResource, f'{basePath}/host/<string:id>')
api.add_resource(SwitchResource, f'{basePath}/switch/<string:id>')
api.add_resource(CableResource, f'{basePath}/cable/<string:id>')
#FIXME: must add also support for switches and cables
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)