import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QIcon, QFont, QPixmap
import pigpio
from pigpio_shell import pigpio_shell as shell
import csv
import time
from numpy import heaviside as u
from Firmware import HAL, Solenoid, SCodeParse

def generateTestFile(file_name, save_vector):
    with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            for row in save_vector:
                writer.writerow(row)
            print(f"Data saved to {file_name}")

def main():
    '''
    generateTestFile("testfile.csv",[
         ['HOME', 'X'],
         ['HOME', 'Y'],
         ['MOVE', 'X40'],
         ['MOVE', 'Y30'],
         ['PUMP', 'On'],
         ['SPRAY', 'On'],
         ['MOVE', 'X-20'],
         ['MOVE', 'Y-20'],
         ['PUMP', 'Off'],
         ['SPRAY', 'Off']
    ])
    generateTestFile("spraytest.csv", [
         [1, 0, 3, 2],
         [1, 1, 1, 1],
         [4, 2]
    ])
    '''

    '''
    log:
    Average distance per 1k steps for 500Hz is 20.116666666666667mm
Average distance per 1k steps for 800Hz is 20.683333333333334mm
Average distance per 1k steps for 1000Hz is 20.250000000000004mm
Average distance per 1k steps for 1600Hz is 0.5mm
Average distance per 1k steps for 2000Hz is 0.0mm
Average distance per 1k steps for 4000Hz is 0.0mm
Average distance per 1k steps for 8000Hz is 0.0mm
avg distance: 20.4mm / 1000 steps

    '''
    data = np.zeros((3, 30))
    test = Solenoid()
    for f in range(11, 14):
        print(f"Now testing frequency {test.PWM_FREQUENCY_LIST[f]}")
        for s in range(30):
            ready = input("Please enter 'y' when ready to start: ")
            if ready == 'y':
                pass
            dir = s % 2
            test.demoMotor(1000, f, dir, 'Y')
            measure = input("Enter measured distance in mm: ")
            data[f-11][s] = float(measure)
            print("Current data: ")
            print(data)
    averaged_data = np.mean(data, axis=1)
    stdev_data = np.std(data, axis=1)
    for f in range(11, 18):
        freq = test.PWM_FREQUENCY_LIST[f]
        mean = averaged_data[f-11]
        stdev = stdev_data[f-11]
        RSD = stdev / mean
        print(f"Distance per 1k steps for {freq}Hz: Mean = {mean}mm | Std = {stdev}mm | RSD = {RSD}mm")
if __name__ == "__main__":
    main()
