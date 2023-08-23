#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from nc_component import ComponentModel, NetworkModel, LinkModel
import os


dir_path = os.path.dirname(os.path.realpath(__file__))
@Gtk.Template(filename=os.path.join(dir_path, "resources/nc_edit_cable.ui"))
class NcEditCable(Gtk.Dialog):
    __gtype_name__ = "NcEditCable"
    
    #can define the named entries in the class
   
    componentA=Gtk.Template.Child('component_A')
    componentB=Gtk.Template.Child('component_B')
    interfaces_A=Gtk.Template.Child('interface_A')
    interfaces_B=Gtk.Template.Child('interface_B')
    img_A=Gtk.Template.Child('img_A')
    img_B=Gtk.Template.Child('img_B')
    def __init__(self, l: LinkModel, parent):
        super().__init__()
        self.cable=l
        self.parent=parent
        
        self.componentA.set_text(l.a.backend_data['name'])
        self.componentB.set_text(l.b.backend_data['name'])

        if l.a.type=='Host':
            self.img_A.set_from_file(os.path.join(dir_path, "resources/host.png"))
        else:
            self.img_A.set_from_file(os.path.join(dir_path, "resources/switch.png"))

        if l.b.type=='Host':
            self.img_B.set_from_file(os.path.join(dir_path, "resources/host.png"))
        else:
            self.img_B.set_from_file(os.path.join(dir_path, "resources/switch.png"))


        intA_model=self.interfaces_A.get_model()
        interfaces=parent.get_interfaces(l.a)
        interfaces.insert(0, interfaces.pop(interfaces.index(l.a_port)))
        for i in interfaces:
            intA_model.append([str(i)])
        self.interfaces_A.set_active(0)

        intB_model=self.interfaces_B.get_model()
        interfaces=parent.get_interfaces(l.b)
        interfaces.insert(0, interfaces.pop(interfaces.index(l.b_port)))
        for i in interfaces:
            intB_model.append([str(i)])
        self.interfaces_B.set_active(0)



        
        
    # Signal handler for the "key-press-event" signal
    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            self.on_ok(None)
  

    @Gtk.Template.Callback()
    def on_ok(self, widget):
        print('save data and close window')
        new_A=int(self.interfaces_A.get_model()[self.interfaces_A.get_active()][0])
        new_B=int(self.interfaces_B.get_model()[self.interfaces_B.get_active()][0])

        if self.cable.a_port != new_A:
            self.parent.switch_ports(self.cable, new_A,self.cable.a_port, a=True)
        
        if self.cable.b_port != new_B:
            self.parent.switch_ports(self.cable, new_B,self.cable.b_port, a=False)
        
        
        self.parent.queue_draw()
        self.destroy()
        
    @Gtk.Template.Callback()
    def on_cancel(self, widget):
        print('close window without saving')
        self.destroy()
