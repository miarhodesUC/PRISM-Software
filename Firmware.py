from pigpio_shell import pigpio_shell as shell
import pigpio 
import csv
import json
import time
from numpy import heaviside as u
import os

# My deepest apologies to any future developers

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
        print(f"Pin {pin} HIGH")

    def setPinLow(self, pin:int):
        self.checkPin(pin, "setPinLow")
        self.pi.write(pin, 0)
        print(f"Pin {pin} LOW")

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
        
    def selectDEMUX(self, selection_index, pin0, pin1): #signaling for demultiplexer
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
                raise ValueError("Error in HAL.selectDEMUX: {} is an invalid selection index, " \
                "check type or make sure it is in range [0, 3]".format(selection_index))
            
    def moveStepperMotor(self, step_pin, direction_pin, direction, duty_cycle, frequency_index):
        if step_pin == direction_pin:
            raise ValueError("Error in HAL.moveStepperMotor: step_pin = {0} = direction_pin = {1}".format(step_pin, direction_pin))
        if direction_pin is not None:
            self.setDirection(direction, direction_pin)
        self.setPWM(step_pin, duty_cycle, frequency_index)
        print(f"Starting motor pin {step_pin} @ frequency {self.PWM_FREQUENCY_LIST[frequency_index]}, dutycycle {duty_cycle}")

    def stopStepperMotor(self, step_pin, direction_pin):
        self.setPinLow(step_pin)
        if direction_pin is not None:
            self.setPinLow(direction_pin)
        print(f"Stopping motor pin {step_pin}")

    def setAsInput(self, pin):
        self.pi.set_mode(pin, 0)

    def setAsOutput(self, pin):
        self.pi.set_mode(pin, 1)

class Solenoid():
    #DIRECTION
    DIRECTION_POSITIVE = 0
    DIRECTION_NEGATIVE = 1

    # Duty cycle
    DUTY_CYCLE_HALF = 128
    PWM_FREQUENCY_LIST = [10, 20, 40, 50, 80, 100, 160, 200, 250, 
                          320, 400, 500, 800, 1000, 1600, 2000, 4000, 8000]
    PWM_FREQUENCY_INDEX = 12
    VALVE_FREQUENCY_INDEX = 12

    # CONSTANT CONFIGS
    STEP_MODE_VALUE = 0.5 #value accounts for stepper motor microsteps
    DISTANCE_PER_STEP = 0.02 #distance in mm per step of the motor

    # PIN CONFIGS
    #TODO Have these configs saved in a JSON file or a txt file
    #INPUTS
    
    EITHER_EDGE = 2
    FALLING_EDGE = 1
    RISING_EDGE = 0
    X_LIMIT_EVENT = 1
    Y_LIMIT_EVENT = 2
    MOVING_LIMIT_EVENT = 3
    '''
     #LOCOMOTIVE MOTORS
    LOCOMOTIVE_DIRECTION_PIN = 17
    DIRECTION_PIN_X = 20
    DIRECTION_PIN_Y = 6
    LOCOMOTIVE_STEP_PIN_X = 12
    LOCOMOTIVE_STEP_PIN_Y = 19
    LOCOMOTIVE_STEP_PIN_T = 5

    X_SWITCH_PIN = 23
    Y_SWITCH_PIN = 24

    #SPRAY MOTOR & VALVES
    PERISTALTIC_STEP_PIN = 13
    RESERVOIR_SELECT_HIGHBIT = 21
    RESERVOIR_SELECT_LOWBIT = 16
    AIR_VALVE_PIN = 26

    '''
    def __init__(self, hal = HAL()):
        self.hal = hal # 'imports' HAL object into this one for using HAL methods
        self.importConfigs("configs.json")
        hal.setAsInput(self.X_SWITCH_PIN)
        hal.setAsInput(self.Y_SWITCH_PIN)
        #TODO (maybe): Add position tracking for soft limit checks
        #TODO (alt idea): distance sensors for tracking distance? (mostly directed at any future capstone groups)

    def importConfigs(self, config_file:str):
        with open(config_file, "r") as file:
            configs = json.load(file)
        self.DIRECTION_PIN_X = configs['motor-pins']['direction-x']
        self.DIRECTION_PIN_Y = configs['motor-pins']['direction-y']
        self.LOCOMOTIVE_STEP_PIN_X = configs['motor-pins']['step-x']
        self.LOCOMOTIVE_STEP_PIN_Y = configs['motor-pins']['step-y']
        self.LOCOMOTIVE_STEP_PIN_T = configs['motor-pins']['step-t']
        self.PERISTALTIC_STEP_PIN = configs['motor-pins']['step-pump']
        self.X_SWITCH_PIN = configs['input-pins']['limit-x']
        self.Y_SWITCH_PIN = configs['input-pins']['limit-y']
        self.RESERVOIR_SELECT_HIGHBIT = configs['valve-pins']['reservoir-hi']
        self.RESERVOIR_SELECT_LOWBIT = configs['valve-pins']['reservoir-lo']
        self.AIR_VALVE_PIN = configs['valve-pins']['air']
        self.PWM_FREQUENCY_INDEX = configs['motor-speed-index']

    def setReservoirSelect(self, reservoir:int): # tooling for selecting coating solution
        self.hal.selectDEMUX(reservoir, self.RESERVOIR_SELECT_LOWBIT, self.RESERVOIR_SELECT_HIGHBIT)

    def demoMotor(self, steps, frequency_index, direction, axis:str): #CAUTION: FOR TESTING PURPOSES ONLY, NOT STOPPED BY LIMITS
        match axis:
            case 'X':
                print("Moving X")
                step_pin = self.LOCOMOTIVE_STEP_PIN_X
                direction_pin = self.DIRECTION_PIN_X
            case 'Y':
                print("Moving Y")
                step_pin = self.LOCOMOTIVE_STEP_PIN_Y
                direction_pin = self.DIRECTION_PIN_Y
            case 'T':
                direction_pin = self.LOCOMOTIVE_DIRECTION_PIN
                step_pin = self.LOCOMOTIVE_STEP_PIN_T
            case _:
                raise ValueError("Error in demoMotor: {} is an invalid axis".format(axis))
        time_value_s = abs(steps) / (self.STEP_MODE_VALUE * 
                                              self.PWM_FREQUENCY_LIST[frequency_index] * self.STEP_MODE_VALUE)
        self.hal.moveStepperMotor(step_pin, direction_pin, 
                                  direction, self.DUTY_CYCLE_HALF, frequency_index)
        time.sleep(time_value_s)
        self.hal.stopStepperMotor(step_pin, direction_pin)

    def moveMotor(self, distance_value, axis:str): # tooling to control motor movements by axis
        match axis:
            case 'X':
                print("Moving X")
                step_pin = self.LOCOMOTIVE_STEP_PIN_X
                direction_pin = self.DIRECTION_PIN_X
                limit_pin = self.X_SWITCH_PIN
            case 'Y':
                print("Moving Y")
                step_pin = self.LOCOMOTIVE_STEP_PIN_Y
                direction_pin = self.DIRECTION_PIN_Y
                limit_pin = self.Y_SWITCH_PIN
            case 'T':
                direction_pin = self.LOCOMOTIVE_DIRECTION_PIN
                step_pin = self.LOCOMOTIVE_STEP_PIN_T
            case _:
                raise ValueError("Error in moveMotor: {} is an invalid axis".format(axis))
        time_value_s = abs(distance_value) / (self.STEP_MODE_VALUE * 
                                              self.PWM_FREQUENCY_LIST[self.PWM_FREQUENCY_INDEX] * self.DISTANCE_PER_STEP)
        self.hal.moveStepperMotor(step_pin, direction_pin, 
                                  u(-distance_value, 0), self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
        if self.hal.pi.wait_for_edge(limit_pin, self.FALLING_EDGE, time_value_s): #times out after desired movement time
            print("Limit switch triggered")
            self.shutdown()
        # time.sleep(time_value_s) # there's probably a better way to do this -> update: there's actually a worse way :3 ^
        self.hal.stopStepperMotor(step_pin, direction_pin)

    def homeMotor(self, axis:str): # resets motors to origin
        match axis:
            case 'X':
                if self.hal.pi.read(self.X_SWITCH_PIN) == 0:
                    print("Already homed")
                    # moves the motor off the limit switch
                    self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.DIRECTION_PIN_X, 
                                  self.DIRECTION_POSITIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                    time.sleep(0.3)
                    self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.DIRECTION_PIN_X)
                    return
                print("Homing X")
                self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.DIRECTION_PIN_X, 
                                  self.DIRECTION_NEGATIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                if self.hal.pi.wait_for_edge(self.X_SWITCH_PIN, self.FALLING_EDGE):
                    print("Limit switch event detected")
                    self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.DIRECTION_PIN_X)
                    # moves the motor off the limit switch
                    self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.DIRECTION_PIN_X, 
                                  self.DIRECTION_POSITIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                    time.sleep(0.3)
                    self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.DIRECTION_PIN_X)
                else:
                    raise TimeoutError("Homing not complete")
            case 'Y':
                if self.hal.pi.read(self.Y_SWITCH_PIN) == 0:
                    print("Already homed")
                    self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.DIRECTION_PIN_Y, 
                                  self.DIRECTION_POSITIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                    time.sleep(0.3)
                    self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.DIRECTION_PIN_Y)
                    return
                print("Homing Y")
                self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.DIRECTION_PIN_Y, 
                                  self.DIRECTION_NEGATIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                if self.hal.pi.wait_for_edge(self.Y_SWITCH_PIN, self.FALLING_EDGE):
                    print("Limit switch event detected")
                    self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.DIRECTION_PIN_Y)
                    self.hal.moveStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.DIRECTION_PIN_Y, 
                                  self.DIRECTION_POSITIVE, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)
                    time.sleep(0.3)
                    self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.DIRECTION_PIN_Y)
                else:
                    raise TimeoutError("Homing not complete")
            case 'T':
                # If a turntable is added, add to this section
                # 'T' corresponds to the theta axis, which would be turning
                print("Homing T not yet implemented")
            case _:    
                raise ValueError("Error in homeMotor: {} is an invalid axis".format(axis))
            
    def pumpOn(self):
        self.hal.moveStepperMotor(self.PERISTALTIC_STEP_PIN, None, 0, self.DUTY_CYCLE_HALF, self.PWM_FREQUENCY_INDEX)

    def pumpOff(self):
        self.hal.stopStepperMotor(self.PERISTALTIC_STEP_PIN, None)

    def openAirValve(self):
        self.hal.setPinHigh(self.AIR_VALVE_PIN)

    def closeAirValve(self):
        self.hal.setPinLow(self.AIR_VALVE_PIN)

    def pwmAirValve(self, pwm_value): #allows air valve to open & close rapidly, maybe don't use this
        self.hal.setPWM(self.AIR_VALVE_PIN, pwm_value, self.VALVE_FREQUENCY_INDEX)

    def shutdown(self): #shutdown sequence for emergencies
        print("Shutting down")
        self.closeAirValve()
        self.pumpOff()
        self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_X, self.DIRECTION_PIN_X)
        self.hal.stopStepperMotor(self.LOCOMOTIVE_STEP_PIN_Y, self.DIRECTION_PIN_Y)
        raise SystemError("Shutdown sequence called")

class SCodeParse():
    # Fluid handling configs, purging is clearing the fluid line, loading is added new solution to the fluid line
    RESERVOIR_TO_VALVE_LENGTH = 1 #dummy value, in mm
    VALVE_TO_NOZZLE_LENGTH = 1 #dummy value, in mm
    FLOW_SPEED = 7.6 # mm/s
    X_LENGTH = 240 # length of nozzle carriage track
    Y_LENGTH = 80 # length of available movement area for baseplate

    def __init__(self, Solenoid = Solenoid()):
        self.motor_solenoid = Solenoid
        self.command_vector = []

    def startSequence(self, coat_vector):
        self.loadCoatCycle(coat_vector)
        self.splitPathFile()
        self.checkPathDisplacement()
        self.executeCoatCycle()
    
    def executeCoatCycle(self):
        self.loadAllFromReservoir()
        for cycle_index in range(self.cycle_count): # iterates through coating routine for the specified number of times
            print(f"Layer {cycle_index} of {self.cycle_count} complete")
            for step_index in range(self.step_count): # iterates through each coating step
                self.motor_solenoid.setReservoirSelect(self.arr_reservoir[step_index])
                self.loadFromSelectedValve()
                self.pathIterator()
                self.commandHOME('X')
                self.commandHOME('Y')
                self.purgeSequence()
    
    def loadCoatCycle(self, coat_vector):
        self.step_count = coat_vector[2][0]
        self.cycle_count = coat_vector[2][1]
        self.arr_reservoir = coat_vector[0]
        self.arr_coat_count = coat_vector[1]
        self.nozzle_path = coat_vector[3][0]

    def splitPathFile(self):
        basepath = os.getcwd()
        pathfile = basepath + "/nozzle_paths/" + self.nozzle_path
        with open(pathfile, "r") as file:
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

    def checkPathDisplacement(self): # ensures that the motors don't try to push the carriage or base plate off the track
        print("Executing path displacement check")
        x_displacement = 0
        y_displacement = 0
        for line_number in range(len(self.command_vector)):
            mneumonic = self.command_vector[line_number][0]
            state = self.command_vector[line_number][1]
            if mneumonic == 'MOVE': #only pulls out the commands that move everything
                try:
                    axis = str(state[0])
                except:
                    raise TypeError(f"Axis value {state[0]} could not be retyped as a string")
                try: 
                    distance_value = int(state[1:])
                except:
                    raise TypeError("Distance value '{}' could not be retyped as an integer".format(state[1:]))
                match axis:
                    case 'X':
                        x_displacement = x_displacement + distance_value
                    case 'Y':
                        y_displacement = y_displacement + distance_value
                    case _:
                        pass
        print(f"Total x_axis displacement: {x_displacement}")
        print(f"Total y_axis displacement: {y_displacement}")
        if x_displacement >= self.X_LENGTH:
            raise ValueError("Baseplate will go out of range, check your path code")
        if y_displacement >= self.Y_LENGTH:
            raise ValueError("Nozzle carriage will go out of range, check your path code")
            
    
    def purgeSequence(self):
        purge_time = self.FLOW_SPEED * self.VALVE_TO_NOZZLE_LENGTH
        self.motor_solenoid.setReservoirSelect(0) # Opens cleaning solution valve
        self.commandPUMP('On') # starts pumping
        self.commandSPRAY('On') # starts spraying
        time.sleep(3 * purge_time) # washes out valve-nozzle line effectively three times 
        self.commandPUMP('Off')
        self.commandSPRAY('Off')

    def loadAllFromReservoir(self):
        load_time = self.FLOW_SPEED * self.RESERVOIR_TO_VALVE_LENGTH
        for open_reservoir in range(4):
            self.motor_solenoid.setReservoirSelect(open_reservoir)
            self.commandPUMP('On') # starts pumping
            time.sleep(load_time) # pumps until fluid reaches valve
            self.commandPUMP('Off')
        self.purgeSequence() # ensures valves are clean

    def loadFromSelectedValve(self):
        load_time = self.FLOW_SPEED * self.VALVE_TO_NOZZLE_LENGTH
        self.commandPUMP('On') # starts pumping
        time.sleep(load_time)
        self.commandSPRAY('On')
        time.sleep(0.5) # sprays for a little to prepare nozzle
        self.commandSPRAY('Off') 
        time.sleep(0.5) # pumps for a little extra to load nozzle
        self.commandPUMP('Off')

    def mneumonicMatch(self, mnemonic, state):
        print("Performing mneumonic match")
        match mnemonic:
            case 'MOVE':
                print("Found case 'MOVE'")
                print(f"State: {state}")
                move_state = state
                self.commandMOVE(move_state)
            case 'PUMP':
                print("Found case 'PUMP'")
                print(f"State: {state}")
                pump_state = state
                self.commandPUMP(pump_state)
            case 'VALV':
                print("Found case 'VALV'")
                print(f"State: {state}")
                valv_state = state
                self.commandVALV(valv_state)
            case 'HOME':
                print("Found case 'HOME'")
                print(f"State: {state}")
                home_state = state
                self.commandHOME(home_state)
            case 'SPRAY':
                print("Found case 'SPRAY'")
                print(f"State: {state}")
                spray_state = state
                self.commandSPRAY(spray_state)
            case _:
                raise ValueError(f"Error in mneumonicMatch: invalid mneumonic {mnemonic}")

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



