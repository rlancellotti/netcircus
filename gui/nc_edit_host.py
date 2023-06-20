#!/usr/bin/python
import gi
import nc_canvas
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from component import ComponentModel, NetworkModel
import os


# Relevant element of an host:
# - Name
# - Description
# - Ram
# - Kernel (from a list)
# - Root FS (from a list)

@Gtk.Template(filename="resources/nc_edit_host.ui")
class NcEditHost(Gtk.Dialog):
    __gtype_name__ = "NcEditHost"
    #can define the named entries in the class
    name=Gtk.Template.Child('name')
    description=Gtk.Template.Child('description')
    memory=Gtk.Template.Child('memory')
    kernel=Gtk.Template.Child('kernel')
    filesystem=Gtk.Template.Child('filesystem')
    def __init__(self, c: ComponentModel, parent):
        super().__init__()
        self.component=c
        self.parent=parent
        # add elements to list of kernels
        #self.kernel.set_entry_text_column(0)
        kernel_model=self.kernel.get_model()
        klist=c.backend.get_kernels()
        for k in klist:
            #kernel_model.append([os.path.basename(k), k])
            kernel_model.append([k])
        # add elements to list of filesystems
        fs_model=self.filesystem.get_model()
        fslist=c.backend.get_filesystems()
        for f in fslist:
            #kernel_model.append([os.path.basename(k), k])
            fs_model.append([f])
        print(self.component.backend_data['id'], self.component.backend_data['name'], self.component.backend_data['description'])
        self.name.set_text(self.component.backend_data['name'])
        self.description.set_text(self.component.backend_data['description'])
        m=self.component.backend_data['mem']
        self.memory.set_value(int(m[0:-1]) if type(m) == str and m.endswith('M') else int(m))
        # FIXME: must select right element in combo box
        for i in range(len(fslist)):
            if fslist[i] == self.component.backend_data['filesystem']:
                self.filesystem.set_active(i)
        for i in range(len(klist)):
            if klist[i] == self.component.backend_data['kernel']:
                self.kernel.set_active(i)
        self.connect("key-press-event", self.on_key_press)

    # Signal handler for the "key-press-event" signal
    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            self.on_ok(None)
    # FIXME: must add all needed signal handlers. If some handler is not needed, remove it from .ui file
    @Gtk.Template.Callback()
    def on_ok(self, widget):
        print('save data and close window')
        # FIXME: management of kernel and filesystem is messed up
        # FIXME 
        self.component.update_backend_data({
            'id': self.component.id, 
            'name': self.name.get_text(),
            'x': self.component.x,
            'y': self.component.y,
            'mem': self.memory.get_value(),
            'kernel': self.kernel.get_model()[self.kernel.get_active()][0],
            'filesystem': self.filesystem.get_model()[self.filesystem.get_active()][0],
            'description': self.description.get_text()
        }, push=True)
        self.parent.queue_draw()
        self.destroy()
        
    @Gtk.Template.Callback()
    def on_cancel(self, widget):
        print('close window without saving')
        self.destroy()
