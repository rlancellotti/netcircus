#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from component import ComponentModel, NetworkModel
import cairo

(COLUMN_TEXT, COLUMN_PIXBUF) = range(2)
DRAG_ACTION = Gdk.DragAction.COPY

@Gtk.Template(filename="nc_canvas.ui")
class NcCanvas(Gtk.DrawingArea):
    __gtype_name__ = "NcCanvas"
    def __init__(self):
        super().__init__()
        self.icons={ComponentModel.TYPE_HOST: cairo.ImageSurface.create_from_png('host.png'),
                    ComponentModel.TYPE_SWITCH: cairo.ImageSurface.create_from_png('switch.png')}
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK) 
        self.network_model=NetworkModel()
        self.current_component=None

    def draw_component(self, cx: cairo.Context, c: ComponentModel):
        #print(f'drawing component @({c.x}, {c.y}, w={self.icons[c.type].get_width()}, h={self.icons[c.type].get_height()}), type={c.type}')
        print(self.icons[c.type])
        cx.set_source_surface(self.icons[c.type], c.x, c.y)
        cx.paint()

    @Gtk.Template.Callback()
    def on_draw(self, widget, cx):
        #print(f'call to draw method widget: {widget}, cairo context: {cr}')
        cx.set_source_rgb(1, 1, 0)
        for c in self.network_model.get_components():
            self.draw_component(cx, c)

    @Gtk.Template.Callback()
    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        print(f'call to on_drag_data_get method widget: {widget}, drag context: {drag_context}, x: {x}, y: {y}, {data.get_text()}')
        comp_type=data.get_text()
        self.add_component(comp_type, x, y)
    
    def add_component(self, comp_type, x, y):
        if comp_type is not None and comp_type != ComponentModel.TYPE_UNKNOWN:
            w=self.icons[comp_type].get_width()
            h=self.icons[comp_type].get_height()
            self.network_model.add_component(comp_type, *icon_coords_from_center(x, y, w, h), w, h)
            self.queue_draw()

    @Gtk.Template.Callback()
    def on_button_press(self, widget, event):
        self.current_component=self.network_model.get_component_from_cords(event.x, event.y)
        if event.button == 1:
            print(f'press @({event.x}, {event.y}) -> {self.current_component}')
        if event.button == 3 and self.current_component is not None:
            print(f'open context menu for component {self.current_component}')

    @Gtk.Template.Callback()
    def on_button_release(self, widget, event):
        if self.current_component is not None:
            c=self.network_model.get_component(self.current_component)
            (c.x, c.y)=icon_coords_from_center(event.x, event.y, c.width, c.height)
            print(f'must move component {self.current_component}')
            self.queue_draw()

def icon_coords_from_center(x, y, w, h):
    return (x-w/2, y-h/2)


if __name__ == '__main__':
    window = Gtk.Window()
    canvas=NcCanvas()
    window.add(canvas)
    canvas.add_component(ComponentModel.TYPE_HOST, 10, 10)
    window.show()
    window.connect("destroy", Gtk.main_quit)
    Gtk.main()

