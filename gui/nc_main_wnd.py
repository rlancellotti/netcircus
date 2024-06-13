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

    def update_load_button_state(self, dialog):
        selected_file = dialog.get_filename()
        if selected_file is not None:
            self.btn_load.set_sensitive(selected_file.endswith(".tgz"))

    @Gtk.Template.Callback()
    def on_action_clicked(self, widget):
        if widget == self.btn_run:
            self.canvas.run_network()
        if widget == self.btn_stop:
            self.canvas.stop_network()
        if widget == self.btn_halt:
            self.canvas.halt_network()
        if widget == self.btn_load:
            # FIXME: rewrite using template
            dialog = Gtk.FileChooserDialog(
                title="Please choose a folder",
                parent=self,
                action=Gtk.FileChooserAction.OPEN,
            )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK
            )
            dialog.set_default_size(800, 400)

            filter_tgz = Gtk.FileFilter()
            filter_tgz.set_name("TGZ files")
            filter_tgz.add_pattern("*.tgz")
            dialog.add_filter(filter_tgz)

            self.btn_load = dialog.get_widget_for_response(Gtk.ResponseType.OK)
            self.btn_load.set_sensitive(False)  # Imposta il pulsante non cliccabile all'inizio

            dialog.connect("selection-changed", self.update_load_button_state)  # Aggiungi il collegamento alla funzione

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                self.canvas.load_network(dialog.get_filename())
            elif response == Gtk.ResponseType.CANCEL:
                print("Cancel clicked")
            dialog.destroy()
        if widget == self.btn_save:
            dialog = Gtk.FileChooserDialog(
                title="Please choose a folder",
                parent=self,
                action=Gtk.FileChooserAction.SAVE,
            )
            dialog.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK
            )
            dialog.set_default_size(800, 400)
            content_area = dialog.get_content_area()
            name_entry = Gtk.Entry()
            name_entry.set_placeholder_text("Enter file name")
            content_area.add(name_entry)  # Aggiungi l'entry all'area di contenuto

            dialog.set_default_size(400, 200)
            dialog.show_all()
            #FIXME: deprected code. Save dialog does not work
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                folder_path = dialog.get_filename()
                file_name = name_entry.get_text()
                #FIXME: must validate path
                #FIXME: must evaluate file name
                print(f'saving to: {folder_path}/{file_name}')
                if not file_name:
                    dialog = Gtk.MessageDialog(
                        parent=self,
                        #modal=True,
                        type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        message_format="Please enter a valid file name."
                    )
                    dialog.run()
                    dialog.destroy()
                else:
                    full_path = f"{folder_path}/{file_name}.tgz"
                    self.canvas.save_network(full_path)
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