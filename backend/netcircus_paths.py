import os
#PATH = os.path.expanduser('~/.local/share/netcircus')
PATH = os.path.expanduser('~/Documenti/Code/NetCircus')
SAVE_PATH = PATH
FS_PATH = PATH + '/image'
KERNEL_PATH = PATH + '/kernel'
WORKAREA = PATH + '/work'
FS1 = FS_PATH + '/root.ext4'
KER1 = "/usr/bin/linux"
KER2 = KERNEL_PATH + '/linux-3.18.20-mod'
KER3 = KERNEL_PATH + '/linux-4.10-mod'

def get_kernels():
    return [KER1, KER2, KER3]

def get_filesystems():
    return [FS1]