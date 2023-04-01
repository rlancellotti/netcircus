#/bin/bash
export FSSIZE=1G
export FSNAME=root.ext4
export PKGLST=packages.txt
export MNTPOINT=/mnt
export ARCH=amd64
export ROOTPWD="root"
export RESDIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )
export UPDATE_ONLY="True"
#export UPDATE_ONLY="False"
if [ "${UPDATE_ONLY}" != "True" ] ; then
    PKG=$(for p in $(head -n-1 ${PKGLST}); do echo -n $p,; done; echo $(tail -n1 ${PKGLST}))
    rm -f ${FSNAME}
    dd if=/dev/zero of=${FSNAME} bs=1 count=1 seek=${FSSIZE}
    /sbin/mkfs.ext4 ${FSNAME}
fi
sudo mount ${FSNAME} ${MNTPOINT} -o loop
if [ "${UPDATE_ONLY}" != "True" ] ; then
    sudo debootstrap --include ${PKG} --arch ${ARCH} stable ${MNTPOINT}
fi
# set default hostname
sudo sh -c "echo uml1 > ${MNTPOINT}/etc/hostname"
# filesystem tuning
sudo sh -c "echo \"/dev/ubda / ext4 errors=remount-ro 0 1\" > ${MNTPOINT}/etc/fstab"
sudo sh -c "echo \"none /run tmpfs defaults,size=64M 0 0\" >> ${MNTPOINT}/etc/fstab"
# Fix systemd to run only one terminal with root autologin      
sudo ln -fs /dev/null ${MNTPOINT}/etc/systemd/system/getty-static.service 
sudo cp "${RESDIR}/getty@.service" "${MNTPOINT}/lib/systemd/system/"
# set password for root
CPWD=$(openssl passwd -1 -salt xy ${ROOTPWD})
sudo sed -i "s/root:\*:/root:${CPWD}:/" ${MNTPOINT}/etc/shadow 
# update .bashrc to have colors and handy aliases
if [ $(sudo grep -v -e "^#" ${MNTPOINT}/root/.bashrc| grep -c -e "alias" |cut -d: -f2) -eq 0 ] ; then
    TMP=${RESDIR}/$$.tmp  
    echo eval \"\$\(dircolors\)\" > $TMP
    echo alias ls=\'ls --color=auto\' >> $TMP
    echo alias d=\'ls --color=auto\' >> $TMP
    echo alias v=\'ls -l --color=auto\' >> $TMP
    sudo sh -c "cat $TMP >> ${MNTPOINT}/root/.bashrc"
    rm $TMP
fi
#sudo ln -s /lib/systemd/system/serial-getty@.service ${MNTPOINT}/etc/systemd/system/getty.target.wants
#sudo rm ${MNTPOINT}/etc/systemd/system/getty.target.wants/getty@tty1.service
sudo umount ${MNTPOINT}
