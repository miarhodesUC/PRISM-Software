import numpy
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QIcon, QFont, QPixmap
import pigpio
from pigpio_shell import pigpio_shell as shell
import csv
import time
from numpy import heaviside as u
from HardwareControls import HAL, MotorSolenoid, SCodeParse

def main():
    test = MotorSolenoid(HAL())
    time_seconds = 5
    time_periods = time_seconds * 10
    test.moveMotor(time_periods, 'X')

if __name__ == "__main__":
    main()
