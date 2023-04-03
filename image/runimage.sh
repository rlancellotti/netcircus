# run with:
# linux ubd0=root.cow,root.ext4 con1=xterm umid=uml1
# other parameters:
# xterm=terminal emulator,title switch,exec switch es: xterm=gnome-terminal,-t,-x'
# hostname=<hostname>
SCRIPTDIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOTFS=${SCRIPTDIR}/root.ext4
COWFILE=${SCRIPTDIR}/root.cow
KERNEL=$(which linux)
HOSTNAME=myuml

if [ ${ROOTFS} -nt ${COWFILE} ]; then
  echo "Removing old COW file: ${COWFILE}"
  rm -f ${COWFILE}
fi
# RUN
#${KERNEL} ubd0=${COWFILE},${ROOTFS} con1=xterm umid=uml1 hostname=test
${KERNEL} ubd0=${COWFILE},${ROOTFS} con1=xterm umid=uml1 hostname=test



