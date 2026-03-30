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

def CarriageSpeedCharacterization():
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

def FlowRateCharacterization():
    data = np.zeros(30)
    test = Solenoid()
    test.pumpOn()
    print("Loading...")
    ready = input("Please enter 'y' when done loading")
    if ready == 'y':
        pass
    for s in range(30):
        ready = input("Please enter 'y' when ready to start: ")
        if ready == 'y':
            pass
        test.pumpOn()
        time.sleep(15)
        test.pumpOff
        print(f"Test #{s+1}")

def FirmwareHardwareCQ():
    test = Solenoid()
    test.homeMotor('X')
    test.homeMotor('Y')
    print("Moving X 30mm")
    test.moveMotor(30, 'X')
    print("Moving Y 40mm")
    test.moveMotor(40, 'Y')
    print("Turning on Pump")
    test.pumpOn()
    test.setReservoirSelect(0)
    time.sleep(2)
    test.setReservoirSelect(1)
    time.sleep(2)
    test.setReservoirSelect(2)
    time.sleep(2)
    test.setReservoirSelect(3)
    test.pumpOff()

def main():
    FirmwareHardwareCQ()

if __name__ == "__main__":
    main()
