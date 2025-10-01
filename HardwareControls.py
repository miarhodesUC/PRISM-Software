import pigpio
import csv
import time
from numpy import heaviside as u
from enum import Enum


class SCodeParse():
    def __init__(self, filename : str, MotorSolenoid):
        self.filename = filename
        self.command_vector = []
        self.motor_solenoid = MotorSolenoid
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
                    move_state = self.command_vector[line_number][1]
                    self.commandMOVE(move_state)
                case 'PUMP':
                    pump_state = self.command_vector[line_number][1]
                    self.commandPUMP(pump_state)
                case 'VALV':
                    valv_state = self.command_vector[line_number][1]
                    self.commandVALV(valv_state)
                case 'HOME':
                    home_state = self.command_vector[line_number][1]
                    self.commandHOME(home_state)
                case _:
                    print("ERROR Invalid keyword on line {}")
                
    def commandHOME(self, state):
        match state[0]:
            case 'X':
                self.motor_solenoid.homeMotorX()
            case 'Y':
                self.motor_solenoid.homeMotorY()
            case 'T':
                self.motor_solenoid.homeMotorT()
            case 'ALL':
                self.motor_solenoid.homeMotorX()
                self.motor_solenoid.homeMotorY()
                self.motor_solenoid.homeMotorT()
            case _:
                print("{} is an invalid state for HOME".format(state[0]))

    def commandMOVE(self, state):
        try: 
            distance_value = int(state[1:])
        except:
            print("Distance value '{}' could not be retyped as an integer".format(state[1:]))
        match state[0]:
            case 'X':
                self.motor_solenoid.moveMotorX(distance_value) 
            case 'Y':
                self.motor_solenoid.moveMotorY(distance_value)
            case 'T':
                self.motor_solenoid.moveMotorT(distance_value)
            case _:
                print("{} is an invalid state for MOVE".format(state[0]))
        
    def commandPUMP(self, state):
        match state:
            case 'Off':
                self.motor_solenoid.pumpOff()
            case '0':
                self.motor_solenoid.pumpOn0()
            case '1':
                self.motor_solenoid.pumpOn1()
            case '2':
                self.motor_solenoid.pumpOn2()
            case '3':
                self.motor_solenoid.pumpOn3()
            case _:
                print("{} is an invalid state for PUMP".format(state))
    def commandVALV(self, state):
        match state:
            case "On":
                self.motor_solenoid.openValve()
            case "Off":
                self.motor_solenoid.closeValve()
            case _:
                duty_cycle = int(state)
                self.motor_solenoid.pwmValve(duty_cycle)


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

class HAL(): # Contains basic GPIO commands
    PWM_FREQUENCY_LIST = [10, 20, 40, 50, 80, 100, 160, 200, 250, 320, 400, 500, 800, 1000, 1600, 2000, 4000, 8000]
    def __init__(self, pi = pigpio.pi()):
        self.pi = pi
    def checkPin(self, pin, method:str):
        if pin < 0:
            print("Error in {}: pin value should be positive".format(method))
            return -1
        if pin > 25:
            print("Error in {}: no exposed GPIO pins greater than 25".format(method))
            return -1
        else:
            pass

    def setPinHigh(self, pin:int):
        self.checkPin(pin, "setPinHigh")
        self.pi.write(pin, 1)

    def setPinLow(self, pin:int):
        self.checkPin(pin, "setPinLow")
        self.pi.write(pin, 0)

    def setPWM(self, pin, duty_cycle:int, frequency_index:int):
        if duty_cycle < 1:
            print("Error in HAL.setPWM: duty cycle should be an integer greater than one \n Check if input is negative or a decimal \n" \
            "If attempting to turn off pwm, use HAL.setPinLow")
            return -1
        if frequency_index < 0:
            print("Error in HAL.setPWM: frequency index cannot be negative")
            return -1
        self.checkPin(pin, "setPWM")
        self.pi.set_PWM_frequency(pin, self.PWM_FREQUENCY_LIST[frequency_index])
        self.pi.set_PWM_dutycycle(pin, duty_cycle)
    def setDirection(self, direction, pin):
        if direction == 1:
            self.setPinHigh(pin)
        elif direction == 0:
            self.setPinLow(pin)
        else:
            print("Error in HAL.setDirection: invalid direction input")
            return -1
    def selectDEMUX(self, selection_index, pin0, pin1):
        match selection_index:
            case 0:
                self.setPinLow(pin0)
                self.setPinLow(pin1)
            case 1:
                self.setPinHigh(pin0)
                self.setPinLow(pin1)
            case 2:
                self.setPinLow(pin0)
                self.setPinHigh(pin1)
            case 3:
                self.setPinHigh(pin0)
                self.setPinHigh(pin1)
            case _:
                print("Error in HAL.selectDEMUX: selection index is invalid, check type or make sure it is in range [0, 3]")
                return -1
    def moveStepperMotor(self, step_pin, direction_pin, direction, selection_index, pin0, pin1, duty_cycle, frequency_index):
        self.setDirection(direction, direction_pin)
        self.selectDEMUX(selection_index, pin0, pin1)
        self.setPWM(step_pin, duty_cycle, frequency_index)

    def stopStepperMotor(self, step_pin):
        self.setPinLow(step_pin)
    
    



class MotorSolenoid():
    # place constants here for pin allocation
    X_SWITCH_PIN = 20
    Y_SWITCH_PIN = 21
    SOLENOID_PIN = 4
    #LOCOMOTIVE MOTORS
    LOCOMOTIVE_DIRECTION_PIN = 22
    LOCOMOTIVE_STEP_PIN = 18
    LOCOMOTIVE_SELECT_HIGHBIT = 27
    LOCOMOTIVE_SELECT_LOWBIT = 17

    #Select values| 00: no motor | 01: motor X | 10: motor Y | 11: motor T
    #PERISTALTIC MOTORS
    PERISTALTIC_STEP_PIN = 13
    PERISTALTIC_SELECT_HIGHBIT = 6
    PERISTALTIC_SELECT_LOWBIT = 5
    
    #DIRECTION
    DIRECTION_POSITIVE = 1
    DIRECTION_NEGATIVE = 0

    # Duty cycle
    DUTY_CYCLE_HALF = 128
    DUTY_CYCLE_QUARTER = 64
    DUTY_CYCLE_OFF = 0

    PWM_FREQUENCY_LIST = [10, 20, 40, 50, 80, 100, 160, 200, 250, 320, 400, 500, 800, 1000, 1600, 2000, 4000, 8000]

    # CONFIGS (Replace when values have been found)
    TIME_CONSTANT = 1
    STEP_MODE_VALUE = 1
    DISTANCE_PER_STEP = 1
    VOLUME_PER_STEP = 1
    def __init__(self, pi = pigpio.pi()):
        self.pi= pi
        self.setFrequency(self.LOCOMOTIVE_DIRECTION_PIN)
        self.setFrequency(self.PERISTALTIC_STEP_PIN)

    def setPinHigh(self, pin : int):
        self.pi.write(pin, 1)

    def setPinLow(self, pin : int):
        self.pi.write(pin, 0)

    def setFrequency(self, step_pin, freq_index=0):
        self.pi.set_PWM_frequency(step_pin, self.PWM_FREQUENCY_LIST[freq_index])
    
    def setLocomotiveSelect(self, axis : str):
        match axis:
            case 'X':
                self.setPinHigh(self.LOCOMOTIVE_SELECT_LOWBIT)
                self.setPinLow(self.LOCOMOTIVE_SELECT_HIGHBIT)
            case 'Y':
                self.setPinLow(self.LOCOMOTIVE_SELECT_LOWBIT)
                self.setPinHigh(self.LOCOMOTIVE_SELECT_HIGHBIT)
            case 'T':
                self.setPinHigh(self.LOCOMOTIVE_SELECT_LOWBIT)
                self.setPinHigh(self.LOCOMOTIVE_SELECT_HIGHBIT)
            case 'Idle':
                self.setPinLow(self.LOCOMOTIVE_SELECT_LOWBIT)
                self.setPinLow(self.LOCOMOTIVE_SELECT_HIGHBIT)

    def setPeristalticSelect(self, pump):
        match pump:
            case '0':
                self.setPinLow()
                self.setPinLow()
            case '1':
                self.setPinHigh()
                self.setPinLow()
            case '2':
                self.setPinLow()
                self.setPinHigh()
            case '3':
                self.setPinHigh()
                self.setPinHigh()
            case _: 
                print("Invalid pump selection")
        
    def moveOneStep(self, step_pin, direction_pin = None, direction = 0):
        #increments motor one step
        if direction:
            self.setPinHigh(direction_pin)
        self.setPinHigh(step_pin)
        self.setPinLow(step_pin)
        if direction:
            self.setPinLow(direction_pin)

    def moveForTime(self, time_value_s, step_pin, direction_pin = None, direction = 0, duty_cycle = DUTY_CYCLE_HALF):
        if direction:
            self.setPinHigh(direction_pin)
        self.pi.set_PWM_dutycycle(step_pin, duty_cycle)
        time.sleep(time_value_s)
        self.setPinLow(step_pin)
        if direction:
            self.setPinLow(direction_pin)

    def moveIndefinitely(self, step_pin, direction_pin = None, direction = 0, duty_cycle = DUTY_CYCLE_HALF):
        if direction:
            self.setPinHigh(direction_pin)
        self.pi.set_PWM_dutycycle(step_pin, duty_cycle)

    def moveStop(self, step_pin, direction_pin = None):
        if direction_pin is not None:
            self.setPinLow(direction_pin)
        self.setPinLow(direction_pin)
    
    def openValve(self):    #TODO MAKE SURE THAT A HIGH SIGNAL IS OPEN AND LOW SIGNAL IS CLOSED
        self.setPinHigh(self.SOLENOID_PIN)

    def closeValve(self):
        self.setPinLow(self.SOLENOID_PIN)

    def pwmValve(self, duty_cycle):
        self.setFrequency(self.SOLENOID_PIN, freq_index = 1)
        self.pi.set_PWM_dutycycle(self.SOLENOID_PIN, duty_cycle)
        
    def moveMotorX(self, distance_value):
        self.setLocomotiveSelect('X')
        time_value_s = abs(distance_value) / (self.STEP_MODE_VALUE * self.pi.get_PWM_frequency(self.LOCOMOTIVE_STEP_PIN) * self.DISTANCE_PER_STEP)
        self.moveForTime(time_value_s, self.LOCOMOTIVE_STEP_PIN, self.LOCOMOTIVE_DIRECTION_PIN, u(distance_value, 0))
    def moveMotorY(self, distance_value):
        self.setLocomotiveSelect('Y')
        time_value_s = abs(distance_value) / (self.STEP_MODE_VALUE * self.pi.get_PWM_frequency(self.LOCOMOTIVE_STEP_PIN) * self.DISTANCE_PER_STEP)
        self.moveForTime(time_value_s, self.LOCOMOTIVE_STEP_PIN, self.LOCOMOTIVE_DIRECTION_PIN, u(distance_value, 0))
    def moveMotorT(self, distance_value):
        self.setLocomotiveSelect('T')
        time_value_s = abs(distance_value) / (self.STEP_MODE_VALUE * self.pi.get_PWM_frequency(self.LOCOMOTIVE_STEP_PIN) * self.DISTANCE_PER_STEP)
        self.moveForTime(time_value_s, self.LOCOMOTIVE_STEP_PIN, self.LOCOMOTIVE_DIRECTION_PIN, u(distance_value, 0))
    def homeMotorX(self):
        self.setLocomotiveSelect('X')
        self.moveIndefinitely(self.LOCOMOTIVE_STEP_PIN, self.LOCOMOTIVE_DIRECTION_PIN, self.DIRECTION_NEGATIVE)
        state = self.pi.read(self.X_SWITCH_PIN)
        while state == 0:   #TODO YOU NEED TO ABSOLUTELY MAKE SURE THIS WORKS
            state = self.pi.read(self.X_SWITCH_PIN)
            if state:
                self.moveStop(self.LOCOMOTIVE_STEP_PIN)

    def homeMotorY(self):
        self.setLocomotiveSelect('Y')
        self.moveIndefinitely(self.LOCOMOTIVE_STEP_PIN, self.LOCOMOTIVE_DIRECTION_PIN, self.DIRECTION_NEGATIVE)
        state = self.pi.read(self.Y_SWITCH_PIN)
        while state == 0:
            state = self.pi.read(self.Y_SWITCH_PIN)
            if state:
                self.moveStop(self.LOCOMOTIVE_STEP_PIN)
    def homeMotorT(self):
        pass
    def pumpOn0(self):
        self.setPeristalticSelect('0')
        self.setFrequency(self.PERISTALTIC_STEP_PIN)
        self.moveIndefinitely(self.PERISTALTIC_STEP_PIN)
    def pumpOn1(self):
        self.setPeristalticSelect('1')
        self.setFrequency(self.PERISTALTIC_STEP_PIN)
        self.moveIndefinitely(self.PERISTALTIC_STEP_PIN)
    def pumpOn2(self):
        self.setPeristalticSelect('2')
        self.setFrequency(self.PERISTALTIC_STEP_PIN)
        self.moveIndefinitely(self.PERISTALTIC_STEP_PIN)
    def pumpOn3(self):
        self.setPeristalticSelect('3')
        self.setFrequency(self.PERISTALTIC_STEP_PIN)
        self.moveIndefinitely(self.PERISTALTIC_STEP_PIN)
    def pumpOff(self):
        self.moveStop(self.PERISTALTIC_STEP_PIN)
        



