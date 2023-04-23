from flask import Flask, request
from flask_restful import Resource, Api
import netcircus_paths
import network
import host

app = Flask(__name__)
api=Api(app)
basePath = '/api/v1'

net=network.Network()

class KernelResource(Resource):
    def get(self):
        return netcircus_paths.get_kernels()

class FilesystemResource(Resource):
    def get(self):
        return netcircus_paths.get_filesystems()

class NetworkResource(Resource):
    def get(self):
        return net.get_name()
    def post(self):
        n=request.json
        # FIXME: must add stronger validation
        if 'name' in n.keys():
            net.set_name(n['name'])
            return net.get_name(), 201
        else: return None, 400

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

api.add_resource(KernelResource, f'{basePath}/system/kernels')
api.add_resource(FilesystemResource, f'{basePath}/system/filesystems')
api.add_resource(NetworkResource, f'{basePath}/system/networkname')
api.add_resource(HostList, f'{basePath}/host')
api.add_resource(HostResource, f'{basePath}/host/<string:id>')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)