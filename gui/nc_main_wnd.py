#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gui.nc_palette import NcPalette
from nc_canvas import NcCanvas


@Gtk.Template(filename="nc_mainwnd.ui")
class NcMainWnd(Gtk.Window):
    __gtype_name__ = "NcMainWnd"
    palette=Gtk.Template.Child('nc_palette')
    canvas=Gtk.Template.Child('nc_canvas')
    def __init__(self):
        super().__init__(title="NetCircus")
        #vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        #self.add(vbox)
        #hbox = Gtk.Box(spacing=12)
        #vbox.pack_start(hbox, True, True, 0)
        #self.palette = NcPalette()
        #self.canvas = NcCanvas()
        print(self.palette, self.canvas)
        self.palette.set_canvas(self.canvas)

        #hbox.pack_start(self.palette, True, True, 0)
        #hbox.pack_start(self.canvas, True, True, 0)
        #self.add_text_targets()

    #def add_text_targets(self):
    #    #self.canvas.drag_dest_set_target_list(None)
    #    #self.palette.drag_source_set_target_list(None)
    #    self.canvas.drag_dest_add_text_targets()
    #    self.palette.drag_source_add_text_targets()

win = NcMainWnd()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
