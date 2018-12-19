#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2013-2018 Hanson Robotics, Ltd, all rights reserved 

import sys
import time
import pygame
import serial

import logging as log
import numpy as np

from imdr4 import sendMotorSpeeds
from retry_decorator import *

class Joystick2IMDR:
    def __init__(self):
        self.serialInterface = '/dev/ttyUSB0'          #RaspberryPi
        #self.serialInterface = '/dev/cu.usbserial-A9YDX7BZ'  #Mac

        # Joystick Axes
        self.fwdAxis = 1
        self.lrAxis = 0
        self.mixButton = 10

        # What value on Joystick before we start moving
        self.deadzone = 0.1
        # Minimum speed
        self.motorCutoff = 0.005

        # Acceleration
        self.acceleration = 0.02

        # Current Velocity
        self.velocity = [0.0,0.0,0.0]
        self.motorSpeed = [0.0,0.0,0.0]

        try:
            self.joystick = self.init_joystick()
            self.serial = serial.Serial(self.serialInterface, 9600, timeout=1)
        except Exception as e:
            log.error(e)
            sys.exit(0)


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

        print joystick.get_numaxes()
        return joystick

    def calculateLinearVelocity(self, dirX, dirY):
        velocity = np.sqrt(np.power(dirX, 2) + np.power(dirY, 2)) * 0.79
        angle = np.arctan2(dirY,-dirX)
        F_a = velocity * np.cos(np.deg2rad(150) - angle)  ## TODO: angles correct?
        F_b = velocity * np.cos(np.deg2rad( 30) - angle)
        F_c = velocity * np.cos(np.deg2rad(270) - angle)
        return [F_a, F_b, F_c]

    def calculateRotationVelocity(self, dirY):
        return [dirY, dirY, dirY]


    def main(self):
        while (True):
            try:
                pygame.event.pump()

                dirX = -self.joystick.get_axis(self.fwdAxis)
                dirY = -self.joystick.get_axis(self.lrAxis)
                dirMix = self.joystick.get_button(self.mixButton) ## TODO: can this be axis on Rapsberry?

                if (np.abs(dirX) < self.deadzone):
                    dirX = 0

                if (np.abs(dirY) < self.deadzone):
                    dirY = 0

                print ""
                log.info("x: " + str(dirX) + " y: " + str(dirY) + " m: " + str(dirMix))

                linVelocity = self.calculateLinearVelocity(dirX, dirY)
                rotVelocity = self.calculateRotationVelocity(dirY)

                ## TODO: this might not be totally right...
                v1 = linVelocity[0] * (1-dirMix) + rotVelocity[0] * dirMix
                v2 = linVelocity[1] * (1-dirMix) + rotVelocity[1] * dirMix
                v3 = linVelocity[2] * (1-dirMix) + rotVelocity[2] * dirMix

                targetVelocity = [v1, v2, v3]

                log.info("lin: " + str(linVelocity) + "\nrot: " + str(rotVelocity) + "\nmix: " + str(targetVelocity))

                # calculate velocity for each motors
                for i in [0, 1, 2]:
                    self.velocity[i] = self.velocity[i] * (1-self.acceleration) + targetVelocity[i] * self.acceleration
                    #self.velocity[i] += - (self.velocity[i] - targetVelocity[i]) * self.acceleration

                    if np.abs(targetVelocity[i])<=0.1:
                        self.velocity[i] *= 0.75
                    
                    self.motorSpeed[i] = self.velocity[i]
                   
                    if (np.abs(self.motorSpeed[i]) < self.motorCutoff) and targetVelocity[i] == 0:
                        self.motorSpeed[i] = 0

                # send speeds to motors via serial
                sendMotorSpeeds(self.serial, self.motorSpeed[0], self.motorSpeed[1], self.motorSpeed[2])

                log.info("target: " + str(targetVelocity) + " actual: " + str(self.motorSpeed))
                time.sleep(0.2)
            except Exception as e:
                log.warning(e)


if __name__ == "__main__":
    sys.tracebacklimit = 0
    log.root.setLevel(log.INFO)
    log.info("joystick2imdr launching...")

    app = Joystick2IMDR()
    app.main()


