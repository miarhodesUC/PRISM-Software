import pigpio
import csv
import time
from enum import Enum


class SCodeParse():
    def __init__(self, filename):
        self.filename = filename
        self.command_vector = []
        pass
    def splitFile(self):
        with open(self.filename, "r") as file:
            content = csv.reader(file)
            for line in content:
                split_line = [s for s in line]
                self.command_vector.append(split_line)
                print(split_line)
    def mneumonicMatch(self):
        for line_number in range(len(self.command_vector)):
            match self.command_vector[line_number][0]:
                case 'MOVE':
                    pass
                case 'PUMP':
                    pass
                case 'COAT':
                    pass
                case 'HOME':
                    pass
                case _:
                    print("ERROR Invalid keyword on line {}")
    def commandHOME(self):
        #switch for axis or ALL
        #each axis will have an associated motor
        #if ALL, move each motor until limit switch

        pass
    def commandMOVE(self):
        #switch for axis
        #each axis will have associated motor

        pass
    def commandPUMP(self):
        #switch for ON or OFF
        #if ON, switch for index
        pass
    def commandCOAT(self):
        # switch for ON or OFF
        pass
    

class I2C():
    I2C_BUS = 1
    def __init__(self, i2c_address):
        self.pi = pigpio.pi()
        self.handle = self.pi.i2c_open(self.I2C_BUS, i2c_address)
        # self.transmit_buffer = []
        # self.receive_buffer = []
    
    def i2cTransmit(self, tx_data):
        error = self.pi.i2c_wsrite_device(self.handle, tx_data)
        print("Transmitting data: {}\n".format(tx_data))
        if error == 0:
            print("SUCCESS")
        else:
            print("FAILED error code: {}".format(error))
        return error
    
    def i2cReceive(self, byte_count):
        rx_data = self.pi.i2c_read_device(self.handle, byte_count)
        return rx_data
    
    def i2cPing(self):
        ping = [] # if this breaks, add a 0 or something
        return self.i2cTransmit(ping)
    
    def i2cReadRegister(self, register_address, byte_count):
        print("Reading register: {}".format(register_address))
        self.i2cTransmit(register_address)
        rx_data = self.i2cReceive(byte_count)
        return rx_data
    
    def i2cWriteRegister(self, register_address, tx_data):
        print("Writing to register: {}".format(register_address))
        self.i2cTransmit(register_address)
        self.i2cTransmit(tx_data)


    






class StepperMotor():
    # place constants here for pin allocation

    #LOCOMOTIVE MOTORS
    LOCOMOTIVE_DIRECTION_PIN = 4
    LOCOMOTIVE_STEP_PIN = 18
    LOCOMOTIVE_SELECT_HIGHBIT = 27
    LOCOMOTIVE_SELECT_LOWBIT = 17

    #PERISTALTIC MOTORS
    PERISTALTIC_STEP_PIN = 13
    PERISTALTIC_SELECT_HIGHBIT = 6
    PERISTALTIC_SELECT_LOWBIT = 5
    
    #DIRECTION
    DIRECTION_LEFT = 0
    DIRECTION_RIGHT = 1

    # Time constant for distance to time calculation
    TIME_CONSTANT = 1
    STEP_MODE_VALUE = 1
    DISTANCE_PER_STEP = 1
    VOLUME_PER_STEP = 1

    # Duty cycle
    DUTY_CYCLE_HALF = 128
    DUTY_CYCLE_QUARTER = 64
    DUTY_CYCLE_OFF = 0

    PWM_FREQUENCY_LIST = [10, 20, 40, 50, 80, 100, 160, 200, 250, 320, 400, 500, 800, 1000, 1600, 2000, 4000, 8000]

    def __init__(self, pi = pigpio.pi()):
        self.pi=pi
    
    def setPinHigh(self, pin : int):
        self.pi.write(pin, 1)

    def setPinLow(self, pin : int):
        self.pi.write(pin, 0)

    def setSpeed(self, step_pin, freq_index):
        self.pi.set_PWM_frequency(step_pin, self.PWM_FREQUENCY_LIST[freq_index])

    def moveOneStep(self, step_pin, direction_pin = None, direction = 0):
        #increments motor one step
        if direction_pin is not None:
            if direction:
                self.setPinHigh(direction_pin)
        self.setPinHigh(step_pin)
        self.setPinLow(step_pin)
        if direction_pin is not None:
            self.setPinLow(direction_pin)

    def moveForTime(self, time_value_ms, step_pin, direction_pin = None, direction = 0):
        #moves motor for set amount of time to achieve a specified time
        #calculate how to move a given distance
        if direction_pin is not None:
            if direction:
                self.setPinHigh(direction_pin)
        self.pi.set_PWM_dutycycle(step_pin, self.DUTY_CYCLE_HALF)
        time.sleep(time_value_ms)
        self.pi.set_PWM_dutycycle(step_pin, 0)

    def moveIndefinitely(self):
        #keep motor moving
        pass
    def moveStop(self):
        #stop motor from moving
        pass
    def moveMotorX(self, distance_value):
        pass

