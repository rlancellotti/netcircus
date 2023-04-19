#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from component import ComponentModel

(COLUMN_TEXT, COLUMN_PIXBUF, COLUMN_TYPE) = range(3)

@Gtk.Template(filename="nc_palette.ui")
class NcPalette(Gtk.IconView):
    __gtype_name__ = "NcPalette"
    #can define the named entries in the class
    #entry = Gtk.Template.Child()
    #button = Gtk.Template.Child()
    def __init__(self):
        super().__init__()
        self.set_text_column(COLUMN_TEXT)
        self.set_pixbuf_column(COLUMN_PIXBUF)
        self.set_model(Gtk.ListStore(str, GdkPixbuf.Pixbuf, str))
        self.add_item("Host", "network-server", ComponentModel.TYPE_HOST)
        self.add_item("Switch", "gnome-modem", ComponentModel.TYPE_SWITCH)
        self.add_item("Cable", "network-wired", ComponentModel.TYPE_UNKNOWN)

        self.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
        self.connect("drag-begin", self.on_drag_begin)
        self.connect("drag-data-get", self.on_drag_data_get)

    def add_item(self, text, icon_name, component):
        pixbuf = Gtk.IconTheme.get_default().load_icon(icon_name, 48, 0)
        self.get_model().append([text, pixbuf, component])

    @Gtk.Template.Callback()
    def on_drag_data_get(self, widget, drag_context, data, info, time):
        print(type(data))
        selected_path = self.get_selected_items()[0]
        selected_iter = self.get_model().get_iter(selected_path)
        value = self.get_model().get_value(selected_iter, COLUMN_TYPE)
        print(f'sending value {value}')
        data.set_text(value, -1)

    @Gtk.Template.Callback()
    def on_drag_begin(self, widget, drag_context):
        #print(f'call to on_drag_begin widget: {widget}, drag context: {drag_context}')
        pass

if __name__ == '__main__':
    window = Gtk.Window()
    palette=NcPalette()
    window.add(palette)
    window.show()
    window.connect("destroy", Gtk.main_quit)
    Gtk.main()