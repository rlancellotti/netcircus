#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from component import ComponentModel
from nc_canvas import NcCanvas

(ACTION_NONE, ACTION_MOVE, ACTION_CONNECT, ACTION_HOST, ACTION_SWITCH) = range(5)

@Gtk.Template(filename="resources/nc_palette.ui")
class NcPalette(Gtk.Bin):
    __gtype_name__ = "NcPalette"
    #can define the named entries in the class
    btn_move=Gtk.Template.Child('btn_move')
    btn_connect=Gtk.Template.Child('btn_connect')
    btn_host=Gtk.Template.Child('btn_host')
    btn_switch=Gtk.Template.Child('btn_switch')

    def __init__(self):
        super().__init__()
        self.buttons={
            ACTION_MOVE: self.btn_move,
            ACTION_CONNECT: self.btn_connect,
            ACTION_HOST: self.btn_host,
            ACTION_SWITCH: self.btn_switch
        }
        self.canvas=None
        self.action=ACTION_MOVE
        self.set_action(self.action)

    def set_canvas(self, canvas: NcCanvas):
        self.canvas=canvas

    def get_action_from_widget(self, widget):
        for action in self.buttons.keys():
            if widget==self.buttons[action]:
                #print(f'identified wiget for action {action}')
                return action

    def is_no_action(self):
        for act in self.buttons.keys():
            if self.buttons[act].get_active():
                return False
        return True
        

    def set_action(self, action):
        #print(f'call to set_action({action}), old status is {self.action}')
        self.action=action
        if self.canvas is not None:
            self.canvas.set_action(action)
        self.buttons[action].set_active(True)
        for act in self.buttons.keys():
            if act != action:
                self.buttons[act].set_active(False)

    @Gtk.Template.Callback()
    def on_toggled(self, widget):
        if widget.get_active():
            action=self.get_action_from_widget(widget)
            self.set_action(action)
        else:
            if self.is_no_action():
                self.set_action(ACTION_MOVE)
        #print(f'toggle: action is: {self.action}')

if __name__ == '__main__':
    window = Gtk.Window()
    palette=NcPalette()
    window.add(palette)
    window.show()
    window.connect("destroy", Gtk.main_quit)
    Gtk.main()