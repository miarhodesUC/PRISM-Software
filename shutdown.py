import numpy as np
from pigpio_shell import pigpio_shell as shell
import csv
import time
from numpy import heaviside as u
from Firmware import HAL, Solenoid, SCodeParse

def shutdown():
    test = Solenoid()
    test.shutdown()
if __name__ == "__main__":
    shutdown()