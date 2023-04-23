#!/bin/bash
echo "*** Test list of kernels and filesystems ***"
GET http://localhost:8080/api/v1/system/kernels
GET http://localhost:8080/api/v1/system/filesystems

echo "*** Test Network name ***"
GET http://localhost:8080/api/v1/system/networkname
echo -n '{"name":"test"}' | POST -c "application/json" 'http://localhost:8080/api/v1/system/networkname'
GET http://localhost:8080/api/v1/system/networkname

echo "*** Create host and get list of hosts ***"
GET http://localhost:8080/api/v1/host
GET http://localhost:8080/api/v1/host/h1
echo -n '{"id":"h1"}' | POST -c "application/json" 'http://localhost:8080/api/v1/host/h1'
GET http://localhost:8080/api/v1/host
GET http://localhost:8080/api/v1/host/h1
lwp-request -m DELETE http://localhost:8080/api/v1/host/h1
GET http://localhost:8080/api/v1/host/h1

