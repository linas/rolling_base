#!/bin/bash

cd "$(dirname "$0")"

# update from git repo
# this assumes RO raspberry pi according to http://hallard.me/raspberry-pi-read-only/
sudo mount -o remount,rw /
sleep 8
git pull
sudo mount -o remount,ro /

# execute script indefinately
while [ 1 ]; do python joystick2dynamixel.py; test $? -gt 0 && break; done