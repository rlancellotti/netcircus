import threading
import subprocess

def launch_backend():
    subprocess.run(['python3', '-m', 'backend.api'])

def launch_gui():
    subprocess.run(['python3', '-m', 'gui.nc_main_wnd'])

if __name__ == '__main__':
    backend_thread = threading.Thread(target=launch_backend)
    backend_thread.start()
    launch_gui()
 
