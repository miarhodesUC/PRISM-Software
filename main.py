import numpy
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QIcon, QFont, QPixmap
import pigpio
from pigpio_shell import pigpio_shell as shell
import csv
import time
from numpy import heaviside as u
from HardwareControls import HAL, Solenoid, SCodeParse

def generateTestFile(file_name, save_vector):
    with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            for row in save_vector:
                writer.writerow(row)
            print(f"Data saved to {file_name}")

def main():
    generateTestFile("testfile.csv",[
         ['HOME', 'X'],
         ['HOME', 'Y'],
         ['MOVE', 'X40'],
         ['MOVE', 'Y30'],
         ['SPRAY', 'On'],
         ['MOVE', 'Y20'],
         ['MOVE', 'X-20'],
         ['MOVE', 'Y-20'],
         ['MOVE', 'X20'],
         ['SPRAY', 'Off']
    ])
    test_session = SCodeParse("testfile.csv", "SavedCycle.csv", Solenoid(HAL(pigpio.pi())))
if __name__ == "__main__":
    main()
