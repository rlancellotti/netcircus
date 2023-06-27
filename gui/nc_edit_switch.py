#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from nc_component import ComponentModel, NetworkModel
import os


# Relevant element of an host:
# - Name
# - Description
# - Ram
# - Kernel (from a list)
# - Root FS (from a list)

dir_path = os.path.dirname(os.path.realpath(__file__))
@Gtk.Template(filename=os.path.join(dir_path, "resources/nc_edit_switch.ui"))
class NcEditSwitch(Gtk.Dialog):
    __gtype_name__ = "NcEditSwitch"
    #can define the named entries in the class
    name=Gtk.Template.Child('name')
    label=Gtk.Template.Child('label')
    n_ports=Gtk.Template.Child('ports')
    is_hub=Gtk.Template.Child('is_hub')
    terminal=Gtk.Template.Child('show_terminal')
    def __init__(self, c: ComponentModel, parent):
        super().__init__()
        self.component=c
        self.parent=parent

        #print(self.component.backend_data['id'], self.component.backend_data['name'], self.component.backend_data['description'])
        self.name.set_text(self.component.backend_data['name'])
        self.label.set_text(self.component.backend_data['label'])
        self.n_ports.set_value(self.component.backend_data['n_ports'])
        self.connect("key-press-event", self.on_key_press)

    # Signal handler for the "key-press-event" signal
    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            self.on_ok(None)
    # FIXME: must add all needed signal handlers. If some handler is not needed, remove it from .ui file
    @Gtk.Template.Callback()
    def on_ok(self, widget):
        print('save data and close window')
        self.component.update_backend_data({
            'id': self.component.id, 
            'name': self.name.get_text(),
            'x': self.component.x,
            'y': self.component.y,
            'n_ports': self.n_ports.get_value(),
            'is_hub': self.is_hub.get_active(),
            'terminal': self.terminal.get_active(),
            'label': self.label.get_text()
        }, push=True)
        self.parent.queue_draw()
        self.destroy()
        
    @Gtk.Template.Callback()
    def on_cancel(self, widget):
        print('close window without saving')
        self.destroy()
