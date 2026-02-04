import pigpio
import serial
from pigpio_shell import pigpio_shell as shell
import csv
import time
from numpy import heaviside as u
from enum import Enum

# To any future programmers looking at this, my deepest apologies


class HAL(): # Contains basic GPIO commands
    PWM_FREQUENCY_LIST = [10, 20, 40, 50, 80, 100, 160, 200, 250, 320, 400, 500, 800, 1000, 1600, 2000, 4000, 8000]
    def __init__(self, pi=pigpio.pi()):
        self.pi = pi
    def checkPin(self, pin, method): # raises errors early
        if type(pin) is not int:
            raise TypeError("checkPin error in {0}, {1} is not an integer".format(method, pin))
        if pin > 31:
            raise ValueError("checkPin error in {0}, {1} is greater than 31".format(method, pin))
        if pin < 0:
            raise ValueError("checkPin error in {0}, {1} is negative".format(method, pin))
    def setPinHigh(self, pin:int):
        self.checkPin(pin, "setPinHigh")
        self.pi.write(pin, 1)
        print(f"Setting GPIO {pin} High")
    def setPinLow(self, pin:int):
        self.checkPin(pin, "setPinLow")
        self.pi.write(pin, 0)
        print(f"Setting GPIO {pin} Low")
    def setPWM(self, pin, duty_cycle:int, frequency_index:int):
        self.checkPin(pin, "setPWM")
        if type(frequency_index) is not int:
            print("Error in HAL.setPWM: {} is an invalid frequency index, indicices should be integers".format(frequency_index))
            raise TypeError
        if frequency_index < 0:
            print("Error in HAL.setPWM: {} is an invalid frequency index, frequency index cannot be negative".format(frequency_index))
            raise ValueError
        if frequency_index > 18:
            print("Error in HAL.setPWM: {} is an invalid frequency index, no frequency indices greater than 17".format(frequency_index))
            raise ValueError
        self.pi.set_PWM_frequency(pin, self.PWM_FREQUENCY_LIST[frequency_index])
        self.pi.set_PWM_dutycycle(pin, duty_cycle)
    def setDirection(self, direction, pin):
        self.checkPin(pin, "setDirection")
        if direction == 1:
            self.setPinHigh(pin)
        elif direction == 0:
            self.setPinLow(pin)
        else:
            raise ValueError("Error in HAL.setDirection: {} is an invalid direction input".format(direction))
    def selectDEMUX(self, selection_index, pin0, pin1):
        if pin0 == pin1:
            raise ValueError("Error in HAL.select DEMUX: pin0 = {0} = pin1 = {1}".format(pin0, pin1))
        self.checkPin(pin0, "selectDEMUX - pin0")
        self.checkPin(pin1, "selectDEMUX - pin1")
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
                raise ValueError("Error in HAL.selectDEMUX: {} is an invalid selection index, check type or make sure it is in range [0, 3]".format(selection_index))
    def moveStepperMotor(self, step_pin, direction_pin, direction, duty_cycle, frequency_index):
        if step_pin == direction_pin:
            raise ValueError("Error in HAL.moveStepperMotor: step_pin = {0} = direction_pin = {1}".format(step_pin, direction_pin))
        if direction_pin is not None:
            self.setDirection(direction, direction_pin)
        self.setPWM(step_pin, duty_cycle, frequency_index)
        print(f"Starting motor pin {step_pin}")
    def stopStepperMotor(self, step_pin, direction_pin):
        self.setPinLow(step_pin)
        self.setPinLow(direction_pin)
        print(f"Stopping motor pin {step_pin}")
    def setAsInput(self, pin):
        self.pi.set_mode(pin, pigpio.INPUT)
    def setAsOutput(self, pin):
        self.pi.set_mode(pin, pigpio.OUTPUT)

class Solenoid():
    #DIRECTION
    DIRECTION_POSITIVE = 0
    DIRECTION_NEGATIVE = 1

    # Duty cycle
    DUTY_CYCLE_HALF = 128
    DUTY_CYCLE_QUARTER = 64
    DUTY_CYCLE_OFF = 0

    PWM_FREQUENCY_LIST = [10, 20, 40, 50, 80, 100, 160, 200, 250, 320, 400, 500, 800, 1000, 1600, 2000, 4000, 8000]
    PWM_FREQUENCY_INDEX = 0
    VALVE_FREQUENCY_INDEX = 1

    # CONSTANT CONFIGS (Replace when values have been found)
    TIME_CONSTANT = 1
    STEP_MODE_VALUE = 1
    DISTANCE_PER_STEP = 1
    VOLUME_PER_STEP = 1

    # PIN CONFIGS
    #TODO Have these configs saved in a JSON file or a txt file
    #INPUTS
    X_SWITCH_PIN = 23
    Y_SWITCH_PIN = 24
    EITHER_EDGE = 2
    FALLING_EDGE = 1
    RISING_EDGE = 0
    X_LIMIT_EVENT = 1
    Y_LIMIT_EVENT = 2

    #LOCOMOTIVE MOTORS
    LOCOMOTIVE_DIRECTION_PIN = 17
    LOCOMOTIVE_STEP_PIN_X = 27
    LOCOMOTIVE_STEP_PIN_Y = 22
    LOCOMOTIVE_STEP_PIN_T = 18

    #SPRAY MOTORS
    PERISTALTIC_STEP_PIN = 13
    RESERVOIR_SELECT_HIGHBIT = 6
    RESERVOIR_SELECT_LOWBIT = 5
    AIR_VALVE_PIN = 25

    def __init__(self, hal = HAL()):
        self.hal = hal # 'imports' HAL object into this one for using HAL methods
        hal.setAsInput(self.X_SWITCH_PIN)
        hal.setAsInput(self.Y_SWITCH_PIN)
        #TODO (maybe): Add position tracking for soft limit checks
        #TODO (alt idea): distance sensors for tracking distance? (mostly directed at any future capstone groups)
    def movingLimitHandling(self, gpio, level, tick): # ensures that motors don't get damaged by moving out of bounds
            print("Limit switch triggered outside of homing routine")
            self.shutdown()
            raise SystemError("Limit switch triggered")
    def homingLimitHandling(self, gpio, level, tick):
        if gpio == self.X_SWITCH_PIN:
            print("X limit triggered")
            self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.LOCOMOTIVE_DIRECTION_PIN)
            self.hal.pi.event_trigger(self.X_LIMIT_EVENT)
        elif gpio == self.Y_SWITCH_PIN:
            print("Y limit triggered")
            self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.LOCOMOTIVE_DIRECTION_PIN)
            self.hal.pi.event_trigger(self.Y_LIMIT_EVENT)
        else:
            print("Unknown callback")
    def setReservoirSelect(self, reservoir:int): # tooling for selecting coating solution
        self.hal.selectDEMUX(reservoir, self.RESERVOIR_SELECT_LOWBIT, self.RESERVOIR_SELECT_HIGHBIT)
    def moveMotor(self, distance_value, axis:str): # tooling to control motor movements by axis
        self.x_limit = self.hal.pi.callback(self.X_SWITCH_PIN, self.FALLING_EDGE, self.movingLimitHandling)
        self.y_limit = self.hal.pi.callback(self.Y_SWITCH_PIN, self.FALLING_EDGE, self.movingLimitHandling)
        match axis:
            case 'X':
                print("Moving X")
                step_pin = self.LOCOMOTIVE_STEP_PIN_X
            case 'Y':
                print("Moving Y")
                step_pin = self.LOCOMOTIVE_STEP_PIN_Y
            case 'T':
                step_pin = self.LOCOMOTIVE_STEP_PIN_T
            case 'Idle':
                print("Idle motor")
            case _:
                raise ValueError("Error in moveMotor: {} is an invalid axis".format(axis))
        time_value_s = abs(distance_value) / (self.STEP_MODE_VALUE * 
                                              self.PWM_FREQUENCY_LIST[self.PWM_FREQUENCY_INDEX] * self.DISTANCE_PER_STEP)
        self.hal.moveStepperMotor(step_pin, self.LOCOMOTIVE_DIRECTION_PIN, 
                                  u(-distance_value, 0), self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
        time.sleep(time_value_s) # there's probably a better way to do this
        self.hal.stopStepperMotor(step_pin, self.LOCOMOTIVE_DIRECTION_PIN)
        self.x_limit.cancel()
        self.y_limit.cancel()
    def homeMotor(self, axis:str): # resets motors to origin
        self.x_limit = self.hal.pi.callback(self.X_SWITCH_PIN, self.FALLING_EDGE, self.homingLimitHandling)
        self.y_limit = self.hal.pi.callback(self.Y_SWITCH_PIN, self.FALLING_EDGE, self.homingLimitHandling)
        match axis:
            case 'X':
                print("Homing X")
                self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.LOCOMOTIVE_DIRECTION_PIN, 
                                  self.DIRECTION_NEGATIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                if self.hal.pi.wait_for_event(self.X_LIMIT_EVENT, 20):
                    print("Limit switch event detected")
                else:
                    raise TimeoutError("Homing not complete")
            case 'Y':
                print("Homing Y")
                self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.LOCOMOTIVE_DIRECTION_PIN, 
                                  self.DIRECTION_NEGATIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                if self.hal.pi.wait_for_event(self.Y_LIMIT_EVENT, 20):
                    print("Limit switch event detected")
                else:
                    raise TimeoutError("Homing not complete")
            case 'T':
                # If a turntable is added, uncomment this section
                # step_pin = self.LOCOMOTIVE_STEP_PIN_T
                # switch_pin = self.T_SWITCH_PIN
                print("Homing T not yet implemented")
            case 'ALL':
                print("Homing all motors")
                self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.LOCOMOTIVE_DIRECTION_PIN, 
                                  self.DIRECTION_NEGATIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                self.hal.pi.wait_for_event(self.X_LIMIT_EVENT, 5)
                self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.LOCOMOTIVE_DIRECTION_PIN, 
                                  self.DIRECTION_NEGATIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                self.hal.pi.wait_for_event(self.Y_LIMIT_EVENT, 5)
            case _:
                raise ValueError("Error in homeMotor: {} is an invalid axis".format(axis))
        self.x_limit.cancel()
        self.y_limit.cancel()
    def pumpOn(self):
        self.hal.moveStepperMotor(self.PERISTALTIC_STEP_PIN, None, 0, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
    def pumpOff(self):
        self.hal.stopStepperMotor(self.PERISTALTIC_STEP_PIN, self.LOCOMOTIVE_DIRECTION_PIN)
    def openAirValve(self):
        self.hal.setPinHigh(self.AIR_VALVE_PIN)
    def closeAirValve(self):
        self.hal.setPinLow(self.AIR_VALVE_PIN)
    def pwmAirValve(self, pwm_value):
        self.hal.setPWM(self.AIR_VALVE_PIN, pwm_value, self.VALVE_FREQUENCY_INDEX)
    def shutdown(self):
        print("Shutting down")
        self.closeAirValve()
        self.pumpOff()
        self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.LOCOMOTIVE_DIRECTION_PIN)
        self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.LOCOMOTIVE_DIRECTION_PIN)
        self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_T, self.LOCOMOTIVE_DIRECTION_PIN)   

class SCodeParse():
    # Fluid handling configs
    PURGE_TIME = 10 #dummy value
    FLUID_LATENCY = 10 #dummy value
    def __init__(self, path_file : str, coating_routine : str, Solenoid = Solenoid()):
        self.pathfile = path_file
        self.routine = coating_routine
        self.command_vector = []
        self.motor_solenoid = Solenoid
        print("Initalization complete, starting coating sequence...")
        self.startSequence()
        print("Complete")

    def startSequence(self):
        self.splitPathFile()
        self.loadCoatCycle()
        self.executeCoatCycle()
    
    def executeCoatCycle(self):
        for cycle_index in range(self.cycle_count): # iterates through coating routine for the specified number of times
            print(f"Layer {cycle_index} of {self.cycle_count} complete")
            for step_index in range(self.step_count): # iterates through each coating step
                self.motor_solenoid.setReservoirSelect(self.arr_reservoir[step_index])
                # need to determine how long pump runs before fluid reaches nozzle
                # also need to determine how long to clear spray
                self.pathIterator()
    
    def loadCoatCycle(self):
        coat_vector = []
        with open(self.routine, "r") as file:
            content = csv.reader(file)
            for line in content:
                int_line = [int(s) for s in line]
                coat_vector.append(int_line)
                print(int_line)
        self.step_count = coat_vector[2][0]
        self.cycle_count = coat_vector[2][1]
        self.arr_reservoir = coat_vector[0]
        self.arr_coat_count = coat_vector[1]

    def splitPathFile(self):
        with open(self.pathfile, "r") as file:
            content = csv.reader(file)
            for line in content:
                split_line = [s for s in line]
                self.command_vector.append(split_line)
                print(split_line)

    def pathIterator(self):
        print("Executing path iterator")
        for line_number in range(len(self.command_vector)):
            print(f"Executing line {line_number}")
            mneumonic = self.command_vector[line_number][0]
            state = self.command_vector[line_number][1]
            self.mneumonicMatch(mneumonic, state)

    def mneumonicMatch(self, mneumonic, state):
        print("Performing mneumonic match")
        match mneumonic:
            case 'MOVE':
                print("Found case 'MOVE'")
                move_state = state
                self.commandMOVE(move_state)
            case 'PUMP':
                print("Found case 'PUMP'")
                pump_state = state
                self.commandPUMP(pump_state)
            case 'VALV':
                print("Found case 'VALV'")
                valv_state = state
                self.commandVALV(valv_state)
            case 'HOME':
                print("Found case 'HOME'")
                home_state = state
                self.commandHOME(home_state)
            case 'SPRAY':
                print("Found case 'SPRAY'")
                spray_state = state
                self.commandSPRAY(spray_state)
            case _:
                raise ValueError(f"Error in mneumonicMatch: invalid mneumonic {mneumonic}")

    def commandHOME(self, state):
        print("Executing command Home")
        self.motor_solenoid.homeMotor(state)

    def commandMOVE(self, state):
        try:
            axis = str(state[0])
        except:
            raise TypeError(f"Axis value {state[0]} could not be retyped as a string")
        try: 
            distance_value = int(state[1:])
        except:
            raise TypeError("Distance value '{}' could not be retyped as an integer".format(state[1:]))
        self.motor_solenoid.moveMotor(distance_value, axis)
        print(f"Moving motor {state[0]} for {distance_value} units")  
   
    def commandPUMP(self, state):
        match state:
            case 'Off':
                self.motor_solenoid.pumpOff()
                print("Pump off")
            case 'On':
                self.motor_solenoid.pumpOn()
                print(f"Pump on")
            case _:
                raise ValueError(f"Pump state {state} is invalid, check pathing code or HardwareControls.Py")

    def commandVALV(self, state):
        #WARNING: Overrides the coating selection done by coat cycle
        try:
            reservoir = int(state)
        except:
            raise TypeError(f"Reservoir {state} is the wrong data type, check pathing code or HardwareControls.Py")
        self.motor_solenoid.setReservoirSelect(reservoir)

    def commandSPRAY(self, state):
        match state:
            case "On":
                self.motor_solenoid.openAirValve()
                print("Opening air compressor valve")
            case "Off":
                self.motor_solenoid.closeAirValve()
                print("Closing air compressor valve")
            case _:
                duty_cycle = int(state)
                self.motor_solenoid.pwmAirValve(duty_cycle)
                print(f"Modulating air compressor at {duty_cycle/255}")

class I2C():
    I2C_BUS = 1
    def __init__(self, i2c_address):
        self.pi = pigpio.pi()
        self.handle = self.pi.i2c_open(self.I2C_BUS, i2c_address)
        # self.transmit_buffer = []
        # self.receive_buffer = []
    
    def i2cTransmit(self, tx_data):
        error = self.pi.i2c_write_device(self.handle, tx_data)
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

