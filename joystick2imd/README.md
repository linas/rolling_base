# pyimdr4

Python module to control the Hangfa IMDR4 Servo Controller on the Discovery Q1 robot base via it's UART and an externally connected PS3 Move controller. Joystick and trigger analog values are mapped to the omniwheel base according to [this paper](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.99.1083&rep=rep1&type=pdf).

## Install

    pip install -r requirements.txt

## Run

    python joystick2imdr.py

## Deployment to Raspberry Pi

### Daemon mode

This could be done nicely as a service but for our purposes we're just gonna put `launch.sh` in `.bashrc`. This assumes Raspberry Pi is setup for readonly mode according to [this guide](http://hallard.me/raspberry-pi-read-only/).

### To pair Sony PS3 navigation controller

See [this guide](https://www.piborg.org/rpi-ps3-help) but modify code to reflect the product id `0x042f`.

## IMDR4 Protocol

This is a reverse-engineering effort to control a Hangfa moving robot base directly from a Raspberry Pi.

Baudrate is 9600. The general format of one message to the servo controller is:

    UART_MSG_PACKAGE_STARTCHAR (0xAA)
    MOTOR_DRIVER_DEVICE_TYPE (0x40)
    MOTOR_DRIVER_ADDRESS (0x01)
    UARTCMD_SetMotorSpeed (41)
    Length of Speed Buffer (8)
    Speed buffer (see below)
    CRC Value (calculated from hash)
    UART_MSG_PACKAGE_ENDCHAR (0x0D)

To set the speed of four motors from four floats (-1...1), first they need to be multiplied by 10000 so that they become signed int16's with the range -10000...10000. After, each of these 16 bit numbers get split into two int8's for transmission, so that Speed Buffer is an array of int8 numbers with length 8.