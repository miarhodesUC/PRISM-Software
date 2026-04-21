import numpy as np
from pigpio_shell import pigpio_shell as shell
import csv
import time
from numpy import heaviside as u
from Firmware import HAL, Solenoid, SCodeParse

def shutdown():
    test = Solenoid()
    test.homeMotor('X')
    test.homeMotor('Y')
    test.moveMotor(100, 'Y')
    test.moveMotor(20, 'X')

if __name__ == "__main__":
    shutdown()