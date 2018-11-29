import classes
import gi
import sys
import cairo

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

"""
    network: define the entire Network box, where we have hosts, switches and other components (see other .py files)
    x,y: two list that define the coordinates points of the button press event (right button)
    flag: list that define the component to draw (0 in case of error,1 host,2 switch,3 cable)
    name: list that contain the name of the component by the user (empty in case of error)

"""
global nameProject
nameProject = "New Project"
network = classes.Network(nameProject)
x = []
y = []
flag = []
name = []
port = []

class MouseButtons:
    LEFT_BUTTON = 1
    RIGHT_BUTTON = 3


# define the drawing process, it's divided by the type number of each component
def draw_component(widget, cr):
    if True:
        for i in range(len(x) - 1):

            if x[i] > 0 and flag[i] == 1:
                # if flag is 1 this is a host
                img = GdkPixbuf.Pixbuf.new_from_file_at_size("host.png", 80, 80)
                Gdk.cairo_set_source_pixbuf(cr, img, x[i], y[i])
                cr.paint()
                cr.set_source_rgb(0.1, 0.1, 0.1)
                cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL,
                                    cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(13)
                cr.move_to(x[i] + 25, y[i] - 10)
                cr.show_text(name[i])

            if x[i] > 0 and flag[i] == 2:
                # if flag is 2 this is a switch
                img = GdkPixbuf.Pixbuf.new_from_file_at_size("switch.png", 80, 80)
                Gdk.cairo_set_source_pixbuf(cr, img, x[i], y[i])
                cr.paint()
                cr.set_source_rgb(0.1, 0.1, 0.1)
                cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL,
                                    cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(13)
                cr.move_to(x[i] + 20, y[i])
                cr.show_text(name[i])

            if x[i] > 0 and flag[i] == 3:
                # if flag is 3 this is a cable connection from point x1,y1 to x2,y2

                pass

    return False


def on_button_press(widget, e):
    if e.type == Gdk.EventType.BUTTON_PRESS \
            and e.button == MouseButtons.RIGHT_BUTTON:
        print("Open options with coordinates")

        try:
            x.append(e.x)
            y.append(e.y)
            optionMouse.show()
        except:
            print("Error INTERNAL 1: \n An error occurred in the mouse press event")

    if e.type == Gdk.EventType.BUTTON_PRESS \
            and e.button == MouseButtons.LEFT_BUTTON:
        try:
            imagePanel.queue_draw()
        except:
            print("Error INTERNAL 2: \n An error occurred in the draw queue ")
    return False


# open errorWindow
def error_window(self, text):
    """
    :param text: The text of error
    :return: The error window that display which error occurred
    """
    if text is None:
        print("Error 0: \n An error occurred in the error window call")
    else:
        errText.set_text(text)
        errWindow.set_title("Error !")
        errWindow.show()


class ClassHandleSignlas:

    # QUIT SIGNALS:

    # quit signal window
    def quit_signal(self):
        sys.exit(0)

    # quit errorWindow
    def quit_error(self):
        errWindow.hide()

    # quit chooser dialog
    def quit_chooser_dialog(self):
        chooserDialog.hide()

    # quit AboutDialog
    def quit_about(self):
        aboutdialog.hide()

    # quit optionMouse window
    def quit_option_mouse(self):
        optionMouse.hide()

    # quit newWindow
    def quit_NP(self):
        newWindow.hide()

    # OTHER SIGNALS:
    # start the network session
    def start_network(self):
        try:
            # check if the network is empty
            if len(network.hosts) > 0 or len(network.switches) > 0:
                network.start()
            else:
                error_window(self, "Error 3: \n An error occurred to starting the network, maybe it's empty network")
        except:
            error_window(self, "Error 1: \n An error occurred to starting the network, "
                               "please look that the network exists")
        return False

    # stop the network session
    def stop_network(self):
        try:
            network.poweroff()
        except:
            error_window(self, "Error 2: \n An error occurred to stop the network, "
                               "please look if the network have some structural problem")
        return False

    # open the AboutDialog
    def about_dialog(self):
        aboutdialog.run()

    # open chooserDialog window
    def open_chooser_dialog(self):
        chooserDialog.show()
        return False

    def option_window(self):
        print("OPTION WINDOW OPEN")
        option_window.show()

    # define the button to create new project
    def new_project_button(self):
        newWindow.show()

    # define the process to create a new project table
    def new_project(self):
        print("NEW PROJECT CREATED")
        text = entry.get_text()
        if len(text) > 0:
            label = Gtk.Label(label=text)
            network = classes.Network(text)
            notebook.remove_page(0)
            notebook.append_page(imagePanel, label)
            newWindow.hide()
        else:
            error_window(self,
                         "Error 9: \n An error occurred in the name of the new project, please find a better name")
        return True

    # define the option for the host addition
    # open_host: method that open the option window about the host
    # add_host: method that create the host in the network class and define the information about

    def add_host(self):

        try:
            print("ADD HOST")
            host = classes.Host(name=hostName.get_text(), label=hostLabel.get_text(), mem=hostMem.get_value_as_int(),
                                project_name=nameProject, n_disks=hostDisk.get_value_as_int(),
                                n_ports=hostPort.get_value_as_int(), kernel=hostKernel.get_active_text(),
                                filesystem=hostFilesystem.get_active_text())
            # check that the name is not empty and is different to other names
            if len(hostName.get_text()) > 0 and name.count(hostName.get_text()) < 1:
                network.add_host(host)
                optionMouse.hide()
                flag.append(1)
                port.append(hostPort.get_value_as_int())
                name.append(hostName.get_text())
            else:
                flag.append(0)
                name.append("")
                port.append(0)
                error_window(self, text="Error 6: \n The name of the host is empty "
                                        "or have same name of another component")

            hostWindow.hide()
        except:
            error_window(self, text="Error 7: \n An error occurred in the host addition")
        return False

    def open_host(self):
        try:
            hostWindow.show()
        except:
            error_window(self, text="Error 8: \n An error occurred in the host option window")
        return False

    def add_hub(self):
        pass

    # Define the option for the switch addition
    # add_switch: method that create the switch in the network class and define it informations
    # open_switch: method that open the option window about the switch

    def add_switch(self):
        try:
            print("ADD SWITCH")
            switch = classes.Switch(name=switchName.get_text(), label=switchLabel.get_text(),
                                    terminal=switchHide.clicked(), n_ports=switchPort.get_value_as_int(), is_hub=False)
            # is_hub TO-DEFINE!
            # check that the name is not empty and is different to other names
            if len(switchName.get_text()) > 0 and name.count(switchName.get_text()) < 1:
                network.add_switch(switch)
                optionMouse.hide()
                flag.append(2)
                port.append(switchPort.get_value_as_int())
                name.append(switchName.get_text())
            else:
                flag.append(0)
                name.append("")
                port.append(0)
                error_window(self, text="Error 12: \n The name of the switch is empty "
                                        "or have same name of another component")

            switchWindow.hide()
        except:
            error_window(self, text="Error 10: \n An error occurred in the switch addition")

        return False

    def open_switch(self):
        try:
            switchWindow.show()
        except:
            error_window(self, text="Error 11: \n An error occurred in the switch option window")
        return False

    # TO-DEFINE!
    # Define the option for the bridge addition
    # : method that create the bridge in the network class and define it information
    # : method that open the option window about the bridge

    def add_bridge(self):
        pass

    # Define the option for the cable addition
    # create_cable: method that create the connection from a component to another
    # open_cable: method that open the window about the switch

    def create_cable(self):
        """
        :param cable: cable class
        :param a: destination a
        :param b: destination b
        :return: the image of cable and the connection inside the list of network
        """
        try:
            print("CREATE CABLE")

            cable = classes.Cable(A=cableFrom.get_active_text(), B=cableTo.get_active_text(),
                                  port_A=cablePortFrom.get_active_text(), port_B=cablePortTo.get_active_text())
            optionMouse.hide()
            network.add_cable(cable)
            flag.append(3)
            name.append("Cable")
            port.append(0)
            cableWindow.hide()
        except:
            error_window(self, text="Error 15: \n An error occurred in the cable creation")

        return False

    def open_cable(self):

        try:
            for i in range(len(x) - 1):
                if flag[i] is 1:
                    cableFrom.append(str(i), name[i])
                elif flag[i] is 2:
                    cableFrom.append(str(i),name[i])
                    cableTo.append(str(i), name[i])
                else:
                    error_window(self,text="Error 17: \n An error occurred in the selection of the component,"
                                           "look if the network is empty or have only host or only switch")

            cableWindow.show()
        except:
            error_window(self, text="Error 16: \n An error occurred in the cable option window")
        return False

    def populate_port(self):
        try:
            for i in range(len(x) - 1):
                if flag[i] is 1:
                    cableFrom.append(str(i), 
        except:
            error_window(self, text="Error 18: \n An error occurred in the cable population process of ports,"
                                    "look if the selected component have almost one port")
        return False

    # ------------------MAIN-----------------
    """

Form: base window  
ClassHandleSinglas: Class that contain all the handlers to managing the application

Here i connected the .glade code with the python code (SimNet.py)
Every variable name is the connection to the handler in the .glade code

    """


abuilder = Gtk.Builder()
abuilder.add_from_file("SimNet.glade")
abuilder.connect_signals(ClassHandleSignlas)
form = abuilder.get_object("Form")

# connect to About Dialog window
aboutdialog = abuilder.get_object("About")

# connect to processStart window
option_window = abuilder.get_object("processStart")

# connect to notebook
notebook = abuilder.get_object("Notebook")

# connect to newProject window
newWindow = abuilder.get_object("newProject")
entry = abuilder.get_object("entryNP")

# connect to errorWindow
errWindow = abuilder.get_object("errorWindow")
errText = abuilder.get_object("errorText")

# connect to ImagePanel
imagePanel = abuilder.get_object("ImagePanel")
imagePanel.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
imagePanel.connect('button-press-event', on_button_press)
imagePanel.connect('draw', draw_component)

# take the info about host
hostWindow = abuilder.get_object("hostWindow")
hostName = abuilder.get_object("hostName")
hostLabel = abuilder.get_object("hostLabel")
hostPort = abuilder.get_object("portHost")
hostMem = abuilder.get_object("memHost")
hostDisk = abuilder.get_object("diskHost")
hostKernel = abuilder.get_object("kernelList")
hostFilesystem = abuilder.get_object("filesystemList")

# take the info about switch
switchWindow = abuilder.get_object("switchWindow")
switchName = abuilder.get_object("switchName")
switchLabel = abuilder.get_object("switchLabel")
switchPort = abuilder.get_object("switchPort")
switchHide = abuilder.get_object("switchHide")

# take the info about cable
cableWindow = abuilder.get_object("cableWindow")
cableFrom = abuilder.get_object("fromCable")
cableTo = abuilder.get_object("toCable")
cablePortFrom = abuilder.get_object("portFrom")
cablePortTo = abuilder.get_object("portTo")

# take the info about otpionMouse
optionMouse = abuilder.get_object("optionMouse")

# take the image icon for the window
imageHost = abuilder.get_object("imageHost")
img = GdkPixbuf.Pixbuf.new_from_file_at_size("host.png", 70, 70)
imageHost.set_from_pixbuf(img)
imageSwitch = abuilder.get_object("imageSwitch")
img = GdkPixbuf.Pixbuf.new_from_file_at_size("switch.png", 70, 70)
imageSwitch.set_from_pixbuf(img)
imageCable = abuilder.get_object("imgCable")
img = GdkPixbuf.Pixbuf.new_from_file_at_size("cable.jpeg", 70, 70)
imageCable.set_from_pixbuf(img)

# connect to the chooserDialog window
chooserDialog = abuilder.get_object("chooserDialog")

# show the entire window
form.show()
Gtk.main()
