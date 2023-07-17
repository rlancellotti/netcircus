#!/usr/bin/python
import os
import subprocess
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0,dir_path)
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from nc_palette import NcPalette
from nc_canvas import NcCanvas

@Gtk.Template(filename=os.path.join(dir_path, "resources/nc_mainwnd.ui"))
class NcMainWnd(Gtk.Window):
    __gtype_name__ = "NcMainWnd"
    palette=Gtk.Template.Child('nc_palette')
    canvas=Gtk.Template.Child('nc_canvas')
    btn_run=Gtk.Template.Child('btn_run')
    btn_stop=Gtk.Template.Child('btn_stop')
    btn_halt=Gtk.Template.Child('btn_halt')
    btn_save=Gtk.Template.Child('btn_save')
    btn_load=Gtk.Template.Child('btn_load')
    def __init__(self):
        super().__init__(title="NetCircus")
        #print(self.palette, self.canvas)
        self.palette.set_canvas(self.canvas)

    @Gtk.Template.Callback()
    def on_action_clicked(self, widget):
        if widget == self.btn_run:
            self.canvas.run_network()
        if widget == self.btn_stop:
            self.canvas.stop_network()
        if widget == self.btn_halt:
            self.canvas.halt_network()
        if widget == self.btn_load:
            dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            )
            dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
            )
            dialog.set_default_size(800, 400)

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                print("Select clicked")
                print("Folder selected: " + dialog.get_filename())
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancel clicked")

            dialog.destroy()

        
        if widget == self.btn_save:
            dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            )
            dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
            )
            dialog.set_default_size(800, 400)

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                print("Select clicked")
                print("Folder selected: " + dialog.get_filename())
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancel clicked")

            dialog.destroy()

    @Gtk.Template.Callback()
    def on_menu_toggled(self, widget):
        print('must toggle properties menu')



win = NcMainWnd()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()