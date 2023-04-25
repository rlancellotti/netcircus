#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from nc_palette import NcPalette
from nc_canvas import NcCanvas


@Gtk.Template(filename="resources/nc_mainwnd.ui")
class NcMainWnd(Gtk.Window):
    __gtype_name__ = "NcMainWnd"
    palette=Gtk.Template.Child('nc_palette')
    canvas=Gtk.Template.Child('nc_canvas')
    btn_run=Gtk.Template.Child('btn_run')
    btn_stop=Gtk.Template.Child('btn_stop')
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

    @Gtk.Template.Callback()
    def on_menu_toggled(self, widget):
        print('must toggle properties menu')

win = NcMainWnd()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
