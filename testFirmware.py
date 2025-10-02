# test file
from HardwareControls import SCodeParse, MotorSolenoid, I2C
import pytest
import pigpio

class HAL_shell():
    PWM_FREQUENCY_LIST = [10, 20, 40, 50, 80, 100, 160, 200, 250, 320, 400, 500, 800, 1000, 1600, 2000, 4000, 8000]
    def __init__(self, pi = pigpio.pi()):
        self.pi = pi
    def checkPin(self, pin, method:str):
        if pin < 0:
            print("Error in {0}: {1} is an invalid pin, pin value should be positive".format(method, pin))
            return -1
        if pin > 25:
            print("Error in {0}: {1} is an invalid pin, no exposed GPIO pins greater than 25 exist".format(method, pin))
            return -1
        else:
            pass
    def setPinHigh(self, pin:int):
        if self.checkPin(pin, "setPinHigh") == -1:
            return -1
        print("Set pin {} high".format(pin))
        return (pin, 1)
    def setPinLow(self, pin:int):
        if self.checkPin(pin, "setPinHigh") == -1:
            return -1
        print("Set pin {} high".format(pin))
        return (pin, 0)
    def setPWM(self, pin, duty_cycle:int, frequency_index:int):
        if duty_cycle < 1:
            print("Error in HAL.setPWM: {} is an invalid duty cycle, duty cycle should be an integer greater than one \n " \
            "Check if input is negative or a decimal \n If attempting to turn off pwm, use HAL.setPinLow".format(duty_cycle))
            return -1
        if frequency_index < 0:
            print("Error in HAL.setPWM: {} is an invalid frequency index, frequency index cannot be negative".format(frequency_index))
            return -1
        if self.checkPin(pin, "setPWM") == -1:
            return -1
        print("Set PWM frequency to {0} and duty cycle to {1}".format(self.PWM_FREQUENCY_LIST[frequency_index], duty_cycle))
        return(pin, duty_cycle, frequency_index)
    def setDirection(self, direction, pin):
        if direction == 1:
            return self.setPinHigh(pin)
        elif direction == 0:
            return self.setPinLow(pin)
        else:
            print("Error in HAL.setDirection: {} is an invalid direction input".format(direction))
            return -1
    def selectDEMUX(self, selection_index, pin0, pin1):
        match selection_index:
            case 0:
                pin0_state = self.setPinLow(pin0)
                pin1_state = self.setPinLow(pin1)
                print("Set: {0} low, {1} low".format(pin0, pin1))
            case 1:
                pin0_state = self.setPinHigh(pin0)
                pin1_state = self.setPinLow(pin1)
                print("Set: {0} high, {1} low".format(pin0, pin1))
            case 2:
                pin0_state = self.setPinLow(pin0)
                pin1_state = self.setPinHigh(pin1)
                print("Set: {0} low, {1} high".format(pin0, pin1))
            case 3:
                pin0_state = self.setPinHigh(pin0)
                pin1_state = self.setPinHigh(pin1)
                print("Set: {0} high, {1} high".format(pin0, pin1))
            case _:
                print("Error in HAL.selectDEMUX: {} is an invalid selection index, check type or make sure it is in range [0, 3]".format(selection_index))
                return -1
        return (pin0_state, pin1_state)
    def moveStepperMotor(self, step_pin, direction_pin, direction, duty_cycle, frequency_index):
        direction_state = None
        if direction_pin is not None:
            direction_state = self.setDirection(direction, direction_pin)
        pwm_state = self.setPWM(step_pin, duty_cycle, frequency_index)
        return (direction_state, pwm_state)
    def stopStepperMotor(self, step_pin):
        return self.setPinLow(step_pin)
    def checkLimitSwitch(self, switch_pin):
        state = self.pi.read(switch_pin)
        return state