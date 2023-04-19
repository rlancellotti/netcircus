class ComponentModel():
    TYPE_HOST = 'Host'
    TYPE_SWITCH = 'Switch'
    TYPE_CABLE = 'Cable'
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

class NetworkModel():
    def __init__(self):
        self.components={}

    def add_component(self, type, x, y, width, height):
        print(f'adding component @({x},{y})')
        c=ComponentModel(type, x, y, width, height)
        self.components[c.id]=c

    def get_components(self):
        return list(self.components.values())
    
    def get_component(self, id):
        return self.components[id] if id in self.components.keys() else None

    def get_component_from_cords(self, x, y):
        for c in reversed(self.get_components()):
            if x>=c.x and x<=(c.x+c.width) and y>=c.y and y<=(c.y+c.height):
                return c.id
        return None
