#!/bin/sh
topology="/vagrant/GNS3/GNS3_ans-v/topology.net"
R1="192.168.3.1"
R2="192.168.2.2"

xvfb-run gns3 $topology &
gns3_pid=$!
# search PGID
gns3_pgid=`ps  h -o  "%r " $gns3_pid | xargs`


echo "waiting 10 sec, for routers loading..."
sleep 10

# loop for ping (connection) test
echo -n "testing connection to $R2 "
while ! (ping -c 1 "${R2}" > /dev/null) ; do
#   sleep 1
  echo -n "."
done
echo "UP"

echo -n "testing connection to $R1 "
while ! (ping -c 1 "${R1}" > /dev/null) ; do
#   sleep 1
  echo -n "."
done
echo "UP"


/vagrant/GNS3/ssh_keys_generate.exp $R2 23 test testtest R2 && echo "ssh on $R2 is UP"
/vagrant/GNS3/ssh_keys_generate.exp $R1 23 test testtest R1 && echo "ssh on $R1 is UP"

echo "to kill GNS3 simulator ===> kill -TERM -$gns3_pgid"
exit 0