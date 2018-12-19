# Copyright (c) 2013-2018 Hanson Robotics, Ltd, all rights reserved. 
# joystick2dynamixel

Simple python scripts to map joystick input to dynamixel servos for movement of robotics platform. Launch script is for internal deployment to Raspberry Pi.

## Install

    pip install -r requirements.txt

## Run

    python joystick2dynamixel.py

## Deployment to Raspberry Pi

### Daemon mode

This could be done nicely as a service but for our purposes we're just gonna put `launch.sh` in `.bashrc`. This assumes Raspberry Pi is setup for readonly mode according to [this guide](http://hallard.me/raspberry-pi-read-only/).

### To pair Sony PS3 navigation controller

See [this guide](https://www.piborg.org/rpi-ps3-help) but modify code to reflect the product id `0x042f`.