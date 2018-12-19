#!/bin/bash
# Copyright (c) 2013-2018 Hanson Robotics, Ltd, all rights reserved 

cd "$(dirname "$0")"

# update from git repo
# this assumes RO raspberry pi according to http://hallard.me/raspberry-pi-read-only/
sudo mount -o remount,rw /
sleep 8
git pull
sudo mount -o remount,ro /

# execute script indefinately
while [ 1 ]; do python joystick2imdr.py; test $? -gt 0 && break; done