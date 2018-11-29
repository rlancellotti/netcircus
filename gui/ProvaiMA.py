import cairo
import gi
from random import randint

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf


class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3

def on_button_press(widget,e):

    if e.type == Gdk.EventType.BUTTON_PRESS \
            and e.button == MouseButtons.RIGHT_BUTTON:
        print("Open options with coordinates")
        x.append(e.x)
        y.append(e.y)
        print(x[-1])
        print(y[-1])
        flag.append(randint(0,1))


    if e.type == Gdk.EventType.BUTTON_PRESS \
            and e.button == MouseButtons.LEFT_BUTTON:
        try:
           a.queue_draw()
           #a.connect('draw',OnDraw)
        except Exception:
            print( "Error INTERNAL 1: \n An error occurred in the mouse press event")
    return False

def OnDraw(w, cr):
    for i in range(len(x)):

        if x[i] > 0 and flag[i] ==1:
            img = GdkPixbuf.Pixbuf.new_from_file_at_size("host.png", 80, 80)
            Gdk.cairo_set_source_pixbuf(cr, img, x[i], y[i])
            cr.paint()

        if x[i] > 0 and flag[i] == 0:
            img = GdkPixbuf.Pixbuf.new_from_file_at_size("switch.png", 80, 80)
            Gdk.cairo_set_source_pixbuf(cr, img, x[i], y[i])
            cr.paint()

w = Gtk.Window()
x = []
y = []
flag = []
x.append(0)
y.append(0)
flag.append(0)
w.set_default_size(640, 480)
a = Gtk.DrawingArea()
a.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
a.connect('button-press-event',on_button_press)
w.add(a)

w.connect('destroy', Gtk.main_quit)
a.connect('draw', OnDraw)

w.show_all()

Gtk.main()