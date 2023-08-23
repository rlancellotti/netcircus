import requests
import psutil
import sys

class ComponentModel():
    TYPE_HOST = 'Host'
    TYPE_SWITCH = 'Switch'
    TYPE_UNKNOWN = ''
    ids=[]
    #next_id=0
    def __init__(self, component_type, x, y, width, height, backend, load=False, backend_data=None):
        self.name = None
        
        #ComponentModel.next_id += 1
        self.type = component_type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        if self.TYPE_HOST==self.type:
            self.free_connect=0
        else:
            self.free_connect=1
        self.backend_data=backend_data
        self.backend=backend
        if not load:
            self.id=f'{component_type}{ComponentModel.get_next_id()}'
            if component_type == ComponentModel.TYPE_HOST:
                backend.add_host(self)
            if component_type == ComponentModel.TYPE_SWITCH:
                backend.add_switch(self)
        else:
            self.id=backend_data['id']
            ComponentModel.ids.append(int(self.id[len(self.type):]))
        print(self.backend_data)
    def new_connection(self):
        rv=self.free_connect
        self.free_connect += 1
        return rv
    def update_backend_data(self, data: dict, push:bool=False):
        if self.backend_data is None:
            self.backend_data=data
        else:
            for k in data.keys():
                self.backend_data[k]=data[k]
        if push:
            self.backend.update_component(self)
    def update_pos(self, x,y):
        self.x=x
        self.y=y
    def get_next_id():
        start=0
        while True:
            if start in ComponentModel.ids:
                start+=1
                continue
            else:
                ComponentModel.ids.append(start)
                return start
    def remove_id(self):
        id= int(self.id[len(self.type):])
        ComponentModel.ids.remove(id)

class LinkModel():
    next_id=0
    def __init__(self, a, b, backend, load=False, backend_data=None):
        LinkModel.next_id += 1
        self.a=a
        self.b=b
        self.backend=backend
        if load:
            self.id=backend_data['id']
            self.a_port=backend_data['port_A']
            self.b_port=backend_data['port_B']
            self.backend_data=backend_data
        else:
            self.id=f'Link{LinkModel.next_id}'
            self.a_port=a.new_connection()
            self.b_port=b.new_connection()
            backend.add_cable(self)
            
    def update_cable(self, data: dict):
        self.a_port=data['a_port']
        self.b_port=data['b_port']
        self.backend.add_cable(self)

class NetworkModel():
    def __init__(self):
        self.components={}
        self.links={}
        self.backend=BackendBridge()


    def init_from_config():
        pass

    def switch_ports(self,c:LinkModel, new_port, old_port, a=True):
        if a:
            component=c.a
            c.a_port=new_port
        else:
            component=c.b
            c.b_port=new_port

        c.backend.add_cable(c)

        for l in self.links.values():
            if l==c:
                continue
            if l.a==component and l.a_port==new_port:
                l.a_port=old_port
                l.backend.add_cable(l)
                break
            if l.b==component and l.b_port==new_port:
                l.b_port=old_port
                l.backend.add_cable(l)
                break




    def add_component(self, component_type, x, y, width, height, load=False, backend_data=None):
        print(f'adding component @({x},{y})')
        c=ComponentModel(component_type, x, y, width, height, backend=self.backend, load=load,backend_data=backend_data)
        self.components[c.id]=c
    
    def add_link(self, a, b, load=False, backend_data=None):
        if type(a) == str:
            a=self.get_component(a)
        if type(b) == str:
            b=self.get_component(b)
        l=LinkModel(a, b, backend=self.backend, load=load, backend_data=backend_data)
        self.links[l.id]=l

    def delete_component(self, c):
        if isinstance(c,ComponentModel):
            cable=False
        elif isinstance(c,LinkModel):
            cable=True
        elif type(c) == str:
            s=c
            c=self.get_component(s)
            if isinstance(c,LinkModel):
                cable=True
            else:
                cable=False
        if cable:
            del(self.links[c.id])
            self.backend.delete_cable(c.id)
        else:
            del(self.components[c.id])
            for l in self.get_links():
                if l.a==c or l.b == c:
                    del self.links[l.id]
            if c.type==ComponentModel.TYPE_HOST:
                self.backend.delete_host(c.id)
                c.remove_id()
            if c.type==ComponentModel.TYPE_SWITCH:
                self.backend.delete_switch(c.id)

    def get_links(self):
        return list(self.links.values())
    
    def get_link(self, id):
        return self.links[id] if id in self.links.keys() else None

    def get_components(self):
        return list(self.components.values())
    
    def get_component(self, id):
        if id in self.components.keys():
            return self.components[id]
        elif id in self.links.keys():
            return self.links[id]
        else:
            return None

    def get_interfaces(self,c:ComponentModel):
        interfaces=[]
        for l in self.links.values():
            if l.a.id == c.id:
                interfaces.append(l.a_port)
            if l.b.id == c.id:
                interfaces.append(l.b_port)
        return interfaces

    def get_component_from_cords(self, x, y):
        for c in reversed(self.get_components()):
            if x>=c.x and x<=(c.x+c.width) and y>=c.y and y<=(c.y+c.height):
                return c.id
        for l in self.get_links():
            x1=l.a.x+l.a.width/2
            x2=l.b.x+l.b.width/2
            y1=l.a.y+l.a.height/2
            y2=l.b.y+l.b.height/2
            numerator = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1)
            denominator = ((y2 - y1)**2 + (x2 - x1)**2)**0.5
            if numerator/denominator<=7:
                return l.id
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
    def update_component(self, h: ComponentModel):
        if h.type==ComponentModel.TYPE_HOST:
            r=requests.post(f'{BackendBridge.base_url}/host/{h.id}', json=h.backend_data)
        if h.type==ComponentModel.TYPE_SWITCH:
            r=requests.post(f'{BackendBridge.base_url}/switch/{h.id}', json=h.backend_data)

    def get_host(self, id: str):
        requests.get(f'{BackendBridge.base_url}/host/{id}')
    def add_switch(self, s: ComponentModel):
            r=requests.post(f'{BackendBridge.base_url}/switch/{s.id}', json={'x': s.x, 'y': s.y, 'width': s.width, 'height': s.height})
            s.update_backend_data(r.json())
    def get_switch(self, id: str):
        requests.get(f'{BackendBridge.base_url}/switch/{id}')

    def delete_host(self, id: str):
        requests.delete(f'{BackendBridge.base_url}/host/{id}')
    def delete_switch(self, id: str):
        requests.delete(f'{BackendBridge.base_url}/switch/{id}')
    def delete_cable(self, id: str):
        requests.delete(f'{BackendBridge.base_url}/cable/{id}')
    def run_network(self):
        requests.post(f'{BackendBridge.base_url}/action/start')
    def stop_network(self):
        requests.post(f'{BackendBridge.base_url}/action/stop')
    def halt_network(self):
        requests.post(f'{BackendBridge.base_url}/action/halt')
    def clean(self):
        requests.post(f'{BackendBridge.base_url}/action/clean')
    def get_kernels(self):
        r=requests.get(f'{BackendBridge.base_url}/system/kernels')
        return r.json()
    def get_filesystems(self):
        r=requests.get(f'{BackendBridge.base_url}/system/filesystems')
        return r.json()
    def add_cable(self, l: LinkModel):
        r=requests.post(f'{BackendBridge.base_url}/cable/{l.id}', json={'endpoint_A':l.a.id ,'port_A': l.a_port,'endpoint_B':l.b.id,'port_B':l.b_port})
    def save_network(self, name):
        requests.post(f'{BackendBridge.base_url}/action/save',json={'name':name})
    def load_network(self, name):
        requests.post(f'{BackendBridge.base_url}/action/load',json={'name':name})
    def get_workarea(self):
        r=requests.get(f'{BackendBridge.base_url}/system/workarea')
        return r.json()