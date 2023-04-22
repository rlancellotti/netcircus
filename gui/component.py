class ComponentModel():
    TYPE_HOST = 'Host'
    TYPE_SWITCH = 'Switch'
    TYPE_UNKNOWN = ''
    next_id=0
    def __init__(self, type, x, y, width, height):
        self.name = None
        self.id=ComponentModel.next_id
        ComponentModel.next_id += 1
        self.type = type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.free_conect=0
    def new_connection(self):
        rv=self.free_conect
        self.free_conect += 1
        return rv

class LinkModel():
    next_id=0
    def __init__(self, a, b):
        self.id=LinkModel.next_id
        LinkModel.next_id += 1
        self.a=a
        self.a_port=a.new_connection()
        self.b=b
        self.b_port=b.new_connection()

class NetworkModel():
    def __init__(self):
        self.components={}
        self.links={}

    def add_component(self, type, x, y, width, height):
        print(f'adding component @({x},{y})')
        c=ComponentModel(type, x, y, width, height)
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
