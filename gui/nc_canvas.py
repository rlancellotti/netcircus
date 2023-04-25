#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from component import ComponentModel, LinkModel, NetworkModel
import cairo

(ACTION_NONE, ACTION_MOVE, ACTION_CONNECT, ACTION_HOST, ACTION_SWITCH) = range(5)

@Gtk.Template(filename="resources/nc_canvas.ui")
class NcCanvas(Gtk.DrawingArea):
    __gtype_name__ = "NcCanvas"
    def __init__(self):
        super().__init__()
        self.icons={ComponentModel.TYPE_HOST: cairo.ImageSurface.create_from_png('resources/host.png'),
                    ComponentModel.TYPE_SWITCH: cairo.ImageSurface.create_from_png('resources/switch.png')}
        #self.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK) 
        self.network_model=NetworkModel()
        self.current_component=None
        self.current_link_start=None
        self.current_link_end=None
        self.action=None
        self.selected_component=None
        self.build_context_menu()
        self.network_model.clean()

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
            self.queue_draw()

    def delete_component(self, widget):
        print(f'deleting component {self.selected_component}')
        self.network_model.delete_component(self.selected_component)
        self.selected_component=None
        self.queue_draw()

    def edit_component(self, widget):
        print(f'editing component {self.selected_component}')

    def update_current_component_pos(self, x, y):
        if self.current_component is not None and self.action==ACTION_MOVE:
            c=self.network_model.get_component(self.current_component)
            (c.x, c.y)=icon_coords_from_center(x, y, c.width, c.height)
            self.queue_draw()

    ############### Actions on network ###############

    def run_network(self):
        self.network_model.backend.run_network()

    def stop_network(self):
        self.network_model.backend.stop_network()

    ############### Callbacks ###############

    @Gtk.Template.Callback()
    def on_motion_notify_event(self, widget, event):
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
                self.current_link_start=self.network_model.get_component_from_cords(event.x, event.y)
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
        for c in self.network_model.get_components():
            self.draw_component(cx, c)
        self.draw_selection(cx)

    ############### Canvas draw ###############

    def draw_component(self, cx: cairo.Context, c: ComponentModel):
        #print(f'drawing component @({c.x}, {c.y}, w={self.icons[c.type].get_width()}, h={self.icons[c.type].get_height()}), type={c.type}')
        #print(self.icons[c.type])
        cx.set_source_surface(self.icons[c.type], c.x, c.y)
        cx.paint()

    def draw_link(self, cx: cairo.Context, l: LinkModel):
        #print(f'drawing component @({c.x}, {c.y}, w={self.icons[c.type].get_width()}, h={self.icons[c.type].get_height()}), type={c.type}')
        cx.set_source_rgb(0, 0, 0)
        cx.move_to(*icon_center(l.a))
        cx.line_to(*icon_center(l.b))
        cx.stroke()
    
    def draw_selection(self, cx):
        if self.selected_component is not None:
            #print(f'drawing selection for component {self.selected_component}')
            c=self.network_model.get_component(self.selected_component)
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

def icon_coords_from_center(x, y, w, h):
    return (x-w/2, y-h/2)

def icon_center(c: ComponentModel):
    return (c.x+c.width/2, c.y+c.height/2)

if __name__ == '__main__':
    window = Gtk.Window()
    canvas=NcCanvas()
    window.add(canvas)
    canvas.add_component(ComponentModel.TYPE_HOST, 10, 10)
    window.show()
    window.connect("destroy", Gtk.main_quit)
    Gtk.main()

