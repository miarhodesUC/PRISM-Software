import numpy as np
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
    for f in range(11, 14):
        freq = test.PWM_FREQUENCY_LIST[f]
        mean = averaged_data[f-11]
        stdev = stdev_data[f-11]
        RSD = stdev / mean
        print(f"Distance per 1k steps for {freq}Hz: Mean = {mean}mm | Std = {stdev}mm | RSD = {RSD}mm")
    '''
    test = Solenoid()
    test.homeMotor('Y')
if __name__ == "__main__":
    main()
