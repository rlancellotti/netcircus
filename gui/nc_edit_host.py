#!/usr/bin/python
import gi
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
    def __init__(self, c: ComponentModel):
        super().__init__()
        self.component=c
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
        # set values for current host
        # FIXME: must select right element in combo box
        # FIXME: must set right value in memory
        print(self.component.backend_data['id'], self.component.backend_data['name'], self.component.backend_data['description'])
        self.name.set_text(self.component.backend_data['name'])
        self.description.set_text(self.component.backend_data['description'])
    def set_filesystems(self, fslist: list):
        pass
    def set_kernels(self, klist: list):
        pass
