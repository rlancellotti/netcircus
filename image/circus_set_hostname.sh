#!/bin/bash
LOG="/root/circus.log"
for i in $(cat /proc/cmdline | tr '\000' ' '); do
    KEY=$(echo $i | cut -d= -f1)
    if [ ${KEY} == "hostname" ] ; then
        HOSTNAME=$(echo $i | cut -d= -f2)
    fi
done
if [ -n "${HOSTNAME}" ] ; then
    hostnamectl --static set-hostname ${HOSTNAME}
    echo "updating hostname: RC=$?" >> ${LOG}
fi
