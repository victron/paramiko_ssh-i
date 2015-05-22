#!/usr/bin/env bash

# add multiverse
add-apt-repository "deb http://archive.ubuntu.com/ubuntu trusty multiverse"
add-apt-repository "deb-src http://archive.ubuntu.com/ubuntu trusty multiverse"
add-apt-repository "deb http://archive.ubuntu.com/ubuntu trusty-updates multiverse"
add-apt-repository "deb-src http://archive.ubuntu.com/ubuntu trusty-updates multiverse"

apt-get update
apt-get install -y gns3
apt-get install -y expect
apt-get install -y tmux
# virtual X server
apt-get install -y xvfb
apt-get install -y python-setuptools
apt-get install -y vsftpd
easy_install pip
pip install paramiko PyYAML Jinja2 httplib2

