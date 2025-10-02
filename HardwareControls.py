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
            mneumonic = self.command_vector[line_number][0]
            match mneumonic:
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
                    print("Error in mneumonicMatch: invalid mneumonic {0} on line {1}".format(mneumonic, line_number))             
    def commandHOME(self, state):
        self.motor_solenoid.homeMotor(state)
    def commandMOVE(self, state):
        try: 
            distance_value = int(state[1:])
        except:
            print("Distance value '{}' could not be retyped as an integer".format(state[1:]))
        self.motor_solenoid.moveMotor(distance_value, state[0])     
    def commandPUMP(self, state):
        match state:
            case 'Off':
                self.motor_solenoid.pumpOff()
            case _:
                try:
                    pump_index = int(state)
                except:
                    print("Error in commandPump:{} could not be retyped as an integer".format(state))
                self.motor_solenoid.pumpOn(pump_index)
    def commandVALV(self, state):
        match state:
            case "On":
                self.motor_solenoid.openValve()
            case "Off":
                self.motor_solenoid.closeValve()
            case _:
                try:
                    duty_cycle = int(state)
                except:
                    print("Error in commandVALV: {} could not be retyped as an integer".format(state))
                self.motor_solenoid.pwmValve(duty_cycle)

class HAL(): # Contains basic GPIO commands
    PWM_FREQUENCY_LIST = [10, 20, 40, 50, 80, 100, 160, 200, 250, 320, 400, 500, 800, 1000, 1600, 2000, 4000, 8000]
    def __init__(self, pi = pigpio.pi()):
        self.pi = pi
    def checkPin(self, pin, method:str): #TODO raise error if any of these fails
        if type(pin) is not int:
            print("Error in {0}: {1} is an invalid pin, pin value should be an integer".format(method, pin))
            return -1
        if pin <= 0:
            print("Error in {0}: {1} is an invalid pin, pin value should be a natural number".format(method, pin))
            return -1
        if pin > 31:
            print("Error in {0}: {1} is an invalid pin, no exposed GPIO pins greater than 31 exist".format(method, pin))
            return -1
        else:
            pass
    def setPinHigh(self, pin:int):
        if self.checkPin(pin, "setPinHigh") == -1:
            return -1
        self.pi.write(pin, 1)
    def setPinLow(self, pin:int):
        if self.checkPin(pin, "setPinLow") == -1:
            return -1
        self.pi.write(pin, 0)
    def setPWM(self, pin, duty_cycle:int, frequency_index:int):
        if type(duty_cycle) is not int:
            print("Error in HAL.setPWM: {} is an invalid duty cycle, duty cycle should be an integer".format(duty_cycle))
            return -1
        if duty_cycle < 1:
            print("Error in HAL.setPWM: {} is an invalid duty cycle, duty cycle should be an integer greater than one \n " \
            "Check if input is negative or a decimal \n If attempting to turn off pwm, use HAL.setPinLow".format(duty_cycle))
            return -1
        if duty_cycle > 255:
            print("Error in HAL.setPWM: {} is an invalid duty cycle, duty cycle should be an integer in range [1, 255] \n ".format(duty_cycle))
        if type(frequency_index) is not int:
            print("Error in HAL.setPWM: {} is an invalid frequency index, indicices should be integers".format(frequency_index))
            return -1
        if frequency_index < 0:
            print("Error in HAL.setPWM: {} is an invalid frequency index, frequency index cannot be negative".format(frequency_index))
            return -1
        if frequency_index > 18:
            print("Error in HAL.setPWM: {} is an invalid frequency index, no frequency indices greater than 17".format(frequency_index))
            return -1
        if self.checkPin(pin, "setPWM") == -1:
            return -1
        self.pi.set_PWM_frequency(pin, self.PWM_FREQUENCY_LIST[frequency_index])
        self.pi.set_PWM_dutycycle(pin, duty_cycle)
    def setDirection(self, direction, pin):
        if direction == 1:
            self.setPinHigh(pin)
        elif direction == 0:
            self.setPinLow(pin)
        else:
            print("Error in HAL.setDirection: {} is an invalid direction input".format(direction))
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
                print("Error in HAL.selectDEMUX: {} is an invalid selection index, check type or make sure it is in range [0, 3]".format(selection_index))
                return -1
    def moveStepperMotor(self, step_pin, direction_pin, direction, duty_cycle, frequency_index):
        if direction_pin is not None:
            self.setDirection(direction, direction_pin)
        self.setPWM(step_pin, duty_cycle, frequency_index)
    def stopStepperMotor(self, step_pin):
        self.setPinLow(step_pin)
    def checkLimitSwitch(self, switch_pin):
        if self.checkPin(switch_pin, "checkLimitSwitch") == -1:
            return -1
        try:
            state = self.pi.read(switch_pin)
        except:
            print("Pin {} does not exist".format(switch_pin))
            return -1
        return state

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
    PWM_FREQUENCY_INDEX = 0
    # CONFIGS (Replace when values have been found)
    TIME_CONSTANT = 1
    STEP_MODE_VALUE = 1
    DISTANCE_PER_STEP = 1
    VOLUME_PER_STEP = 1
    def __init__(self, hal = HAL()):
        self.hal = hal
    def setLocomotiveSelect(self, axis:int):
        self.hal.selectDEMUX(axis, self.LOCOMOTIVE_SELECT_LOWBIT, self.LOCOMOTIVE_SELECT_HIGHBIT)
    def setPeristalticSelect(self, pump:int):
        self.hal.selectDEMUX(pump, self.PERISTALTIC_SELECT_LOWBIT, self.PERISTALTIC_SELECT_HIGHBIT)
    def moveMotor(self, distance_value, axis:str):
        match axis:
            case 'X':
                self.setLocomotiveSelect(1)
            case 'Y':
                self.setLocomotiveSelect(2)
            case 'T':
                self.setLocomotiveSelect(3)
            case 'Idle':
                self.setLocomotiveSelect(0)
        time_value_s = abs(distance_value) / (self.STEP_MODE_VALUE * 
                                              self.PWM_FREQUENCY_LIST[self.PWM_FREQUENCY_INDEX] * self.DISTANCE_PER_STEP)
        self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN, self.LOCOMOTIVE_DIRECTION_PIN, 
                                  u(distance_value, 0), self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
        time.sleep(time_value_s)
        self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN)
    def homeMotor(self, axis:str):
        match axis:
            case 'X':
                self.setLocomotiveSelect(1)
                switch_pin = self.X_SWITCH_PIN
            case 'Y':
                self.setLocomotiveSelect(2)
                switch_pin = self.Y_SWITCH_PIN
            case 'T':
                # self.setLocomotiveSelect(3)
                # switch_pin = self.T_SWITCH_PIN
                print("Homing T not yet implemented")
                return 0
            case 'All':
                self.setLocomotiveSelect(1)
                self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN, self.LOCOMOTIVE_DIRECTION_PIN, 
                                  self.DIRECTION_NEGATIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                state = 0
                while state == 0:
                    state = self.hal.checkLimitSwitch(switch_pin)
                    if state == 1:
                        self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN)
                self.setLocomotiveSelect(2)
                self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN, self.LOCOMOTIVE_DIRECTION_PIN, 
                                  self.DIRECTION_NEGATIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                state = 0
                while state == 0:
                    state = self.hal.checkLimitSwitch(switch_pin)
                    if state == 1:
                        self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN)
                return 0
            case _:
                print("Error in homeMotor: {} is an invalid axis".format(axis))
        self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN, self.LOCOMOTIVE_DIRECTION_PIN, 
                                  self.DIRECTION_NEGATIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
        state = 0
        while state == 0:
            state = self.hal.checkLimitSwitch(switch_pin)
            if state == 1:
                self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN)
    def pumpOn(self, pump):
        self.setPeristalticSelect(pump)
        self.hal.moveStepperMotor(self.PERISTALTIC_STEP_PIN, None, 0, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
    def pumpOff(self):
        self.moveStop(self.PERISTALTIC_STEP_PIN)

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



