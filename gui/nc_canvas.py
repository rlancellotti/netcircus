#!/usr/bin/python
import json
import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from nc_component import ComponentModel, LinkModel, NetworkModel
from nc_edit_host import NcEditHost
from nc_edit_switch import NcEditSwitch
from nc_edit_cable import NcEditCable
import cairo

(ACTION_NONE, ACTION_MOVE, ACTION_CONNECT, ACTION_HOST, ACTION_SWITCH) = range(5)

dir_path = os.path.dirname(os.path.realpath(__file__))
@Gtk.Template(filename=os.path.join(dir_path, "resources/nc_canvas.ui"))
class NcCanvas(Gtk.DrawingArea):
    __gtype_name__ = "NcCanvas"
    def __init__(self):
        super().__init__()
        self.icons={ComponentModel.TYPE_HOST: cairo.ImageSurface.create_from_png(os.path.join(dir_path, "resources/host.png")),
                    ComponentModel.TYPE_SWITCH: cairo.ImageSurface.create_from_png(os.path.join(dir_path, "resources/switch.png"))}
        #self.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK | Gdk.EventMask.POINTER_MOTION_MASK) 
        self.network_model=NetworkModel()
        self.current_component=None
        self.current_link_start=None
        self.current_link_end=None
        self.action=None
        self.selected_component=None
        self.build_context_menu()
        self.network_model.clean()
        self.edit_host_dialog=None
        self.edit_switch_dialog=None


    def build_context_menu(self):
        self.cmenu = Gtk.Menu.new()
        menucontent={'Delete': self.delete_component,
                     'Edit': self.edit_component}
        for mi in menucontent.keys():
            item=Gtk.MenuItem.new_with_label(mi)
            item.connect('activate', menucontent[mi])
            self.cmenu.append(item)
        self.cmenu.show_all()

    def set_action(self, action):
        self.action=action

    ############### Component+Link management ###############

    def add_component(self, comp_type, x, y):
        if comp_type is not None and comp_type != ComponentModel.TYPE_UNKNOWN:
            w=self.icons[comp_type].get_width()
            h=self.icons[comp_type].get_height()
            self.network_model.add_component(comp_type, *icon_coords_from_center(x, y, w, h), w, h)
            self.selected_component=self.network_model.get_component_from_cords(x,y)
            
            if comp_type==ComponentModel.TYPE_HOST or comp_type==ComponentModel.TYPE_SWITCH:
                self.edit_component(None)
           
            self.queue_draw()

    def delete_component(self, widget):
        print(f'deleting component {self.selected_component}')
        self.network_model.delete_component(self.selected_component)
        self.selected_component=None
        self.queue_draw()

    def edit_component(self, widget):
        print(f'editing component {self.selected_component}')
        component=self.network_model.get_component(self.selected_component)
        if isinstance(component,ComponentModel):
            if component.type==ComponentModel.TYPE_HOST:
                self.edit_host_dialog=NcEditHost(component,self)
                self.edit_host_dialog.show_all()
            if component.type==ComponentModel.TYPE_SWITCH:
                self.edit_switch_dialog=NcEditSwitch(component,self)
                self.edit_switch_dialog.show_all()
        if isinstance(component,LinkModel):
            self.edit_cable_dialog=NcEditCable(component,self)
            self.edit_cable_dialog.show_all()

    def update_current_component_pos(self, x, y):            
        if self.current_component is not None and self.action==ACTION_MOVE and isinstance(self.network_model.get_component(self.current_component),ComponentModel):
            c=self.network_model.get_component(self.current_component)
            (c.x, c.y)=icon_coords_from_center(x, y, c.width, c.height)
            # FIXME: send update also to backend
            self.queue_draw()

    ############### Actions on network ###############

    def run_network(self):
        self.network_model.backend.run_network()

    def stop_network(self):
        self.network_model.backend.stop_network()
        
    def halt_network(self):
        self.network_model.backend.halt_network()
    
    #FIXME: add action halt network!

    ############### Callbacks ###############


    def host_focused(self,x,y):
        for i in self.network_model.components.values():
            if i.type==ComponentModel.TYPE_HOST:
                #print(f'x={i.x} y={i.y} w={i.width} h={i.height} mx={x} my{y}')
                if i.x <= x <=i.x+i.width and i.y <= y <=i.y+i.height:
                   return i.id
        return None


    @Gtk.Template.Callback()
    def on_motion_notify_event(self, widget, event):
        focused=self.host_focused(event.x, event.y)
        if focused:
            tooltip_text = self.network_model.components[focused].backend_data['description']
            Gtk.Widget.set_tooltip_text(widget, split_string(tooltip_text,30))
            Gtk.Widget.trigger_tooltip_query(widget)
        else:
            Gtk.Widget.set_tooltip_text(widget, None)

        if self.current_component is not None:
            #print('motion: updating component pos')
            self.update_current_component_pos(event.x, event.y)
        if self.current_link_start is not None:
            #print('motion: updating dangling link')
            self.current_link_end=(event.x, event.y)
            self.queue_draw()

    #@Gtk.Template.Callback()
    #def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
    #    print(f'call to on_drag_data_get method widget: {widget}, drag context: {drag_context}, x: {x}, y: {y}, {data.get_text()}')
    #    comp_type=data.get_text()
    #    self.add_component(comp_type, x, y)
        
    @Gtk.Template.Callback()
    def on_button_press(self, widget, event):
        if event.button == 1:
            if self.action==ACTION_MOVE:
                self.current_component=self.network_model.get_component_from_cords(event.x, event.y)
                self.selected_component=self.network_model.get_component_from_cords(event.x, event.y)
            if self.action==ACTION_CONNECT:
                start=self.network_model.get_component_from_cords(event.x, event.y)
                if isinstance(self.network_model.get_component(start),ComponentModel):
                    self.current_link_start=start
                #print(f'connect from @({event.x}, {event.y}) -> {self.current_link_start}')
            if self.action==ACTION_HOST:
                self.add_component(ComponentModel.TYPE_HOST, event.x, event.y)
                self.selected_component=self.network_model.get_component_from_cords(event.x, event.y)
            if self.action==ACTION_SWITCH:
                self.add_component(ComponentModel.TYPE_SWITCH, event.x, event.y)
                self.selected_component=self.network_model.get_component_from_cords(event.x, event.y)
        if event.button == 3:
            #self.build_context_menu()
            self.selected_component=self.network_model.get_component_from_cords(event.x, event.y)
            #print(f'pressedd button3: selected component is: {self.selected_component}')
            self.cmenu.popup_at_pointer()
        self.queue_draw()

    @Gtk.Template.Callback()
    def on_button_release(self, widget, event):
        if self.current_component is not None and self.action==ACTION_MOVE:
            self.update_current_component_pos(event.x, event.y)
            self.current_component=None
        if self.current_link_start is not None and self.action==ACTION_CONNECT:
            cb=self.network_model.get_component_from_cords(event.x, event.y)
            if cb is not None and cb != self.current_link_start:
                self.network_model.add_link(self.current_link_start, cb)
            self.queue_draw()
            self.current_link_start=None
            self.current_link_end=None

    @Gtk.Template.Callback()
    def on_draw(self, widget, cx):
        #print(f'call to draw method widget: {widget}, cairo context: {cr}')
        self.draw_dangling_link(cx)
        for l in self.network_model.get_links():
            self.draw_link(cx, l)
        self.draw_link_selection(cx)
        for c in self.network_model.get_components():
            self.draw_component(cx, c)
        self.draw_selection(cx)

    ############### Canvas draw ###############

    def draw_component(self, cx: cairo.Context, c: ComponentModel):
        #print(f'drawing component @({c.x}, {c.y}, w={self.icons[c.type].get_width()}, h={self.icons[c.type].get_height()}), type={c.type}')
        #print(self.icons[c.type])
        cx.set_source_surface(self.icons[c.type], c.x, c.y)
        cx.paint()
        # FIXME: show name of component: improve choice of font and size, improve positioning. desciption should be on the row below the name in smaller font
        if c.backend_data is not None and 'name' in c.backend_data.keys():
            cx.set_font_size(15)
            (x, y, width, height, dx, dy) = cx.text_extents(c.backend_data['name'])  #getting text size
            color=self.get_style_context().get_color(Gtk.StateFlags.NORMAL)         #getting the right color     
            cx.move_to(c.x + c.width/2 - width/2, c.y-10)
            cx.set_source_rgb(color.red,color.green,color.blue)
            cx.show_text(c.backend_data['name'])

    def draw_link(self, cx: cairo.Context, l: LinkModel, selected=False):
        #print(f'drawing component @({c.x}, {c.y}, w={self.icons[c.type].get_width()}, h={self.icons[c.type].get_height()}), type={c.type}')
        if selected:
            cx.set_source_rgb(1, 0, 0)
        else:
            cx.set_source_rgb(65/255,111/255, 168/255)
        cx.move_to(*icon_center(l.a))
        cx.line_to(*icon_center(l.b))
        cx.stroke()
        # FIXME: write port number
        self.draw_port_name(cx, l , True)
        self.draw_port_name(cx, l , False)

    def  draw_port_name(self, cx, l, a):
        if a:
            k=find_port_position(icon_center(l.a),icon_center(l.b), l.a.width, l.a.height)
            port=l.a_port
        else:
            k=find_port_position(icon_center(l.b),icon_center(l.a), l.a.width, l.a.height, reverse=True)
            port=l.b_port
        color=self.get_style_context().get_color(Gtk.StateFlags.NORMAL) 
        cx.move_to(k[0],k[1])
        cx.set_source_rgb(color.red,color.green,color.blue)
        cx.set_font_size(15)
        cx.show_text(str(port))



    def draw_link_selection(self, cx):
        if self.selected_component is not None:
            l=self.network_model.get_link(self.selected_component)
            if  isinstance(l,LinkModel):
                self.draw_link(cx,l,True)
    
    def draw_selection(self, cx):
        if self.selected_component is not None:
            #print(f'drawing selection for component {self.selected_component}')
            c=self.network_model.get_component(self.selected_component)
            if isinstance(c,ComponentModel):
                cx.set_source_rgb(1, 0, 0)
                cx.rectangle(c.x, c.y, c.width, c.height)
                cx.stroke()
            
    def draw_dangling_link(self, cx: cairo.Context):
        #print('call to draw_dangling_link')
        if self.current_link_start is not None and self.current_link_end is not None:
            #print(f'drawing danging link from {icon_center(self.network_model.get_component(self.current_link_start))} to {self.current_link_end}')
            cx.set_source_rgb(0.5, 0.5, 0.5)
            cx.move_to(*icon_center(self.network_model.get_component(self.current_link_start)))
            cx.line_to(*self.current_link_end)
            cx.stroke()

    def save_network(self,name):
        self.network_model.backend.save_network(name)

    def load_network(self,name):
        self.network_model.backend.load_network(name)
        workarea=self.network_model.backend.get_workarea()
        with open(workarea + '/config.json', 'r') as f:
            conf=json.load(f)
            for h in conf['hosts']:
                self.network_model.add_component('Host', h['x'],h['y'], h['width'], h['height'], load=True, backend_data=h)
            for s in conf['switches']:
                self.network_model.add_component('Switch', s['x'],s['y'], s['width'], s['height'], load=True, backend_data=s)
            for c in conf['cables']:
                self.network_model.add_link(c['endpoint_A'],c['endpoint_B'] , load=True,backend_data=c)
        self.queue_draw()


    def get_interfaces(self,c:ComponentModel):
        return self.network_model.get_interfaces(c)
        
    def switch_ports(self,c:LinkModel, new_port, old_port, a=True):
        return self.network_model.switch_ports(c,new_port,old_port,a)
           


def icon_coords_from_center(x, y, w, h):
    return (x-w/2, y-h/2)

def icon_center(c: ComponentModel):
    return (c.x+c.width/2, c.y+c.height/2)

def find_point_on_segment(A, B, D):
    vector_AB = (B[0] - A[0], B[1] - A[1])
    length_AB = ((vector_AB[0]) ** 2 + (vector_AB[1]) ** 2) ** 0.5
    
    P_x = A[0] + (D / length_AB) * vector_AB[0]
    P_y = A[1] + (D / length_AB) * vector_AB[1]
    
    return P_x, P_y

def find_perpendicular_point(P, A, B, D, reverse=False):
    AB = (B[0] - A[0], B[1] - A[1])
    length_AB = ((AB[0]) ** 2 + (AB[1]) ** 2) ** 0.5
    normalized_AB = (AB[0] / length_AB, AB[1] / length_AB)
    if not reverse:
        perpendicular_vector = (-normalized_AB[1], normalized_AB[0])
    else:
        perpendicular_vector = (normalized_AB[1], -normalized_AB[0])
    PK = (perpendicular_vector[0] * D, perpendicular_vector[1] * D)
    K = (P[0] + PK[0], P[1] + PK[1])
    
    return K

def find_port_position(a, b, w, h, reverse=False):
    P = find_point_on_segment(a, b, max(w,h)/2+30)
    K = find_perpendicular_point(P, a, b, 14, reverse=reverse)
    return K

def split_string(string, max_characters):       #splits a string in different lines 
    if len(string) <= max_characters:
        return string

    result = []
    current_line = ""

    words = string.split()

    for word in words:
        if len(current_line + word) <= max_characters:
            current_line += word + " "
        else:
            result.append(current_line.rstrip())
            current_line = word + " "

    # Add the last line if necessary
    if current_line:
        result.append(current_line.rstrip())

    return "\n".join(result)

if __name__ == '__main__':
    window = Gtk.Window()
    canvas=NcCanvas()
    window.add(canvas)
    canvas.add_component(ComponentModel.TYPE_HOST, 10, 10)
    window.show()
    window.connect("destroy", Gtk.main_quit)
    Gtk.main()

