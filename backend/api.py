from flask import Flask, request
from flask_restful import Resource, Api
import netcircus_paths
import network
import host

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
            net.save()
            return None, 200
        # FIXME: must implement 'load' action

api.add_resource(SystemResource, f'{basePath}/system/<string:res>')
api.add_resource(ActionResource, f'{basePath}/action/<string:action>')
api.add_resource(HostList, f'{basePath}/host')
api.add_resource(HostResource, f'{basePath}/host/<string:id>')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)