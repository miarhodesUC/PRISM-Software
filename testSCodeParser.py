import HAL_shell
from HardwareControls import SCodeParse, motor_solenoid_shell
from pigpio_shell import pigpio_shell as pi
import csv
import time
import pytest
from numpy import heaviside as u

def generateTestFile(file_name, save_vector):
    with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            for row in save_vector:
                writer.writerow(row)
            print(f"Data saved to {file_name}")

def test_env():
    generateTestFile("testfile.csv",[
         ['HOME', 'ALL'],
         ['MOVE', 'X10'],
         ['MOVE', 'Y5'],
         ['VALV', 'On'],
         ['PUMP', '3'],
         ['MOVE', 'T200'],
         ['PUMP', 'Off'],
         ['VALV', 'Off'],
    ])
    parser = SCodeParse("testfile.csv", motor_solenoid_shell())
    parser.splitFile()
    parser.mneumonicMatch()

test_env()