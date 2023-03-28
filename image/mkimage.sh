#/bin/bash
export FSSIZE=1G
export FSNAME=root.ext4
export PKGLST=packages.txt
export MNTPOINT=/mnt
export ARCH=amd64
export ROOTPWD="root"
export RESDIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )
echo $RESDIR
PKG=$(for p in $(head -n-1 ${PKGLST}); do echo -n $p,; done; echo $(tail -n1 ${PKGLST}))
rm -f ${FSNAME}
dd if=/dev/zero of=${FSNAME} bs=1 count=1 seek=${FSSIZE}
/sbin/mkfs.ext4 ${FSNAME}
sudo mount ${FSNAME} ${MNTPOINT} -o loop
sudo debootstrap --include ${PKG} --arch ${ARCH} stable ${MNTPOINT}
# set default hostname
sudo sh -c "echo uml1 > ${MNTPOINT}/etc/hostname"
# filesystem tuning
sudo sh -c "echo \"/dev/ubda / ext4 errors=remount-ro 0 1\" >> ${MNTPOINT}/etc/fstab"
sudo sh -c "echo \"none /run tmpfs defaults,size=64M 0 0\" >> ${MNTPOINT}/etc/fstab"
# FIXME: remove getty-static.service from services to execute
# sudo cp getty-static.service ${MNTPOINT}/usr/lib/systemd/system/
# set password for root
CPWD=$(openssl passwd -1 -salt xy ${ROOTPWD})
sudo sed -i "s/root:\*:/root:${CPWD}:/" ${MNTPOINT}/etc/shadow 
# must set console on kernel command line: con=xterm
# must leave just one tty
sudo ln -s /dev/null ${MNTPOINT}/etc/systemd/system/getty-static.service 
#sudo ln -s /lib/systemd/system/serial-getty@.service ${MNTPOINT}/etc/systemd/system/getty.target.wants
#sudo rm ${MNTPOINT}/etc/systemd/system/getty.target.wants/getty@tty1.service
sudo umount ${MNTPOINT}
# modify iniittab
# must add: 
# 0:2345:respawn:/sbin/gettyorblock -a root 38400 tty0 xterm
# T0:2345:respawn:/sbin/gettyorblock -a root -L ttyS0 9600 xterm
#cp ${RESDIR}/inittab ${MNTPOINT}/etc/inittab
# add tty0 and ttyS0 to /etc/securetty
# run with:
# linux ubd0=root.cow,root.ext4 con1=xterm umid=uml1
# other parameters:
# xterm=terminal emulator,title switch,exec switch es: xterm=gnome-terminal,-t,-x'
# hostname=<hostname>