import requests
import psutil
import sys

class ComponentModel():
    TYPE_HOST = 'Host'
    TYPE_SWITCH = 'Switch'
    TYPE_UNKNOWN = ''
    next_id=0
    def __init__(self, component_type, x, y, width, height, backend):
        self.name = None
        self.id=f'{component_type}{ComponentModel.next_id}'
        ComponentModel.next_id += 1
        self.type = component_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.free_connect=0
        self.backend_data=None
        self.backend=backend
        if component_type == ComponentModel.TYPE_HOST:
            backend.add_host(self)
        print(self.backend_data)
    def new_connection(self):
        rv=self.free_connect
        self.free_connect += 1
        return rv
    def update_backend_data(self, data):
        self.backend_data=data
    def update_pos(self, x,y):
        self.x=x
        self.y=y

class LinkModel():
    next_id=0
    def __init__(self, a, b):
        self.id=f'Link{LinkModel.next_id}'
        LinkModel.next_id += 1
        self.a=a
        self.a_port=a.new_connection()
        self.b=b
        self.b_port=b.new_connection()
    def update_backend_data(self, data):
        #FIXME: To implement
        self.backend_data=data

class NetworkModel():
    def __init__(self):
        self.components={}
        self.links={}
        self.backend=BackendBridge()

    def add_component(self, component_type, x, y, width, height):
        print(f'adding component @({x},{y})')
        c=ComponentModel(component_type, x, y, width, height, backend=self.backend)
        self.components[c.id]=c
    
    def add_link(self, a, b):
        if type(a) == int:
            a=self.get_component(a)
        if type(b) == int:
            b=self.get_component(b)
        l=LinkModel(a, b)
        self.links[l.id]=l

    def delete_component(self, c):
        if type(c) == int:
            c=self.get_component(c)
        del(self.components[c.id])
        for l in self.get_links():
            if l.a==c or l.b == c:
                del self.links[l.id]

    def get_links(self):
        return list(self.links.values())
    
    def get_link(self, id):
        return self.links[id] if id in self.links.keys() else None

    def get_components(self):
        return list(self.components.values())
    
    def get_component(self, id):
        return self.components[id] if id in self.components.keys() else None

    def get_component_from_cords(self, x, y):
        for c in reversed(self.get_components()):
            if x>=c.x and x<=(c.x+c.width) and y>=c.y and y<=(c.y+c.height):
                return c.id
        return None

    def clean(self):
        # FIXME: must ensure that the current model is cleaned
        self.backend.clean()

class BackendBridge:
    base_url='http://localhost:8080/api/v1'
    def __init__(self):
        # FIXME: Check if backend is available
        started=False
        for c in psutil.net_connections():
            if c.status == psutil.CONN_LISTEN and c.laddr == ('127.0.0.1', 8080):
                started=True
        if not started:
            #FIXME: must start backend if it is not started
            print('backend not started. Must stop now.')
            sys.exit()
    def add_host(self, h: ComponentModel):
        r=requests.post(f'{BackendBridge.base_url}/host/{h.id}', json={'x': h.x, 'y': h.y, 'width': h.width, 'height': h.height})
        h.update_backend_data(r.json())
    def get_host(self, id):
        requests.get(f'{BackendBridge.base_url}/host/{id}')
    def run_network(self):
        requests.post(f'{BackendBridge.base_url}/action/start')
    def stop_network(self):
        requests.post(f'{BackendBridge.base_url}/action/stop')
    def clean(self):
        requests.post(f'{BackendBridge.base_url}/action/clean')
