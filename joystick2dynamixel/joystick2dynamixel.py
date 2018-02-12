#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import pygame

import logging as log
import numpy as np

from retry_decorator import *
from dynamixel_driver import dynamixel_io

class Joystick2Dynamixel:
    def __init__(self):
        self.dynamixelInterface = '/dev/ttyUSB0'

        # Dynamixel Servo IDs
        self.leftMotor = 31
        self.rightMotor = 30

        # Joystick Axes
        self.fwdAxis = 1
        self.lrAxis = 0

        # What value on Joystick before we start moving
        self.deadzone = 0.1
        # Minimum speed on dynamixels
        self.dynamixelCutoff = 5

        # Acceleration
        self.acceleration = 0.05

        # Current Velocity
        self.velocity = [0.0,0.0]
        self.dynamixelSpeed = [0,0]

        try:
            self.joystick = self.init_joystick()
            self.dynamixel = self.init_dynamixel()
        except Exception as e:
            log.error(e)
            sys.exit(0)
        

    @retry(Exception, tries = 5, timeout_secs = 0.5)
    def init_dynamixel(self):
        dynamixel = dynamixel_io.DynamixelIO(self.dynamixelInterface, 1000000)

        # wait for servo to connect...
        time.sleep(1.5)

        # see if both motors respond
        if (len(dynamixel.ping(self.leftMotor))==0 or len(dynamixel.ping(self.rightMotor))==0) :
            raise Exception('Servo not found...')

        return dynamixel

    @retry(Exception, tries = 2, timeout_secs = 1.5)
    def init_joystick(self):
        pygame.init()

        # Set up the joystick
        pygame.joystick.init()

        joystick = None
        joystick_names = []

        # Enumerate joysticks
        for i in range(0, pygame.joystick.get_count()):
            joystick_names.append(pygame.joystick.Joystick(i).get_name())

        log.info("connecting to " + str(joystick_names))

        # By default, load the first available joystick.
        if (len(joystick_names) > 0):
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
        else:
            raise Exception('Joystick not found...')

        return joystick


    def setSpeedLeft(self, speed):
        self.dynamixel.set_speed(self.leftMotor, speed)

    def setSpeedRight(self, speed):
        self.dynamixel.set_speed(self.rightMotor, speed)

    def calculateDifferentialDrive(self,dirX,dirY):
        if (np.abs(dirX) < self.deadzone):
            dirX = 0

        if (np.abs(dirY) < self.deadzone):
            dirY = 0

        mag = np.sqrt(np.power(dirX,2) + np.power(dirY,2))
        left = np.maximum(np.minimum(dirX - dirY,1),-1)
        right = np.maximum(np.minimum(dirX + dirY,1),-1)

        return [left,right]

    def main(self):
        while (True):
            try:
                pygame.event.pump()

                dirX = -self.joystick.get_axis(self.fwdAxis)
                dirY = -self.joystick.get_axis(self.lrAxis)

                targetVelocity = self.calculateDifferentialDrive(dirX, dirY)

                # calculate velocity for each motors
                for i in [0, 1]:
                    self.velocity[i] += - (self.velocity[i] - targetVelocity[i]) * self.acceleration
                    self.dynamixelSpeed[i] = int(np.floor(self.velocity[i] * 512))
                    
                    if (np.abs(self.dynamixelSpeed[i]) < self.dynamixelCutoff):
                        self.dynamixelSpeed[i] = 0

                self.setSpeedLeft(self.dynamixelSpeed[0])
                self.setSpeedRight(-self.dynamixelSpeed[1])

                log.info("target: " + str(targetVelocity) + " actual: " + str(self.dynamixelSpeed))
                time.sleep(0.1)
            except dynamixel_io.DroppedPacketError:
                log.warning("Dropped package to dynamixel motor...")


if __name__ == "__main__":
    sys.tracebacklimit = 0
    log.root.setLevel(log.INFO)
    log.info("joystick2dynamixel launching...")

    app = Joystick2Dynamixel()
    app.main()


