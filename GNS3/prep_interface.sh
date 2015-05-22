#!/bin/sh
ip tuntap add dev tap1 mode tap user vagrant
#tunctl -t tap1 -u
ip addr add 192.168.2.1/24 dev tap1
ifconfig tap1 up
route add -net 192.168.0.0/16 dev tap1
