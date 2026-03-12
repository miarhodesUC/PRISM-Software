# test file
from Firmware import SCodeParse, MotorSolenoid
from HAL_shell import HAL_shell
import pigpio
import csv
import time
import pytest
from numpy import heaviside as u

@pytest.fixture 
def hal():
    return HAL_shell()

def test_setPinHigh(hal):
    assert hal.setPinHigh(10) == (10, 1), "Setting pin 10 high should yield a value of 1"
    assert hal.setPinHigh(24) == (24, 1), "Setting pin 24 high should yield a value of 1"
    assert hal.setPinHigh(0) == -1
    assert hal.setPinHigh(-1) == -1, "Pin -1 does not exist and should yield the error code -1"
    assert hal.setPinHigh(26) == -1, "Pin 26 does not exist and should yield the error code -1"
    assert hal.setPinHigh(0.5) == -1, "Non integer pins are not allowed"
    assert hal.setPinHigh(1.5) == -1, "Non integer pins are not allowed"

def test_setPinLow(hal):
    assert hal.setPinLow(10) == (10, 0), "Setting pin 10 low should yield a value of 0"
    assert hal.setPinLow(24) == (24, 0), "Setting pin 24 low should yield a value of 0"
    assert hal.setPinLow(-1) == -1, "Pin -1 does not exist and should yield the error code -1"
    assert hal.setPinLow(26) == -1, "Pin 26 does not exist and should yield the error code -1"
    assert hal.setPinLow(0.5) == -1, "Non integer pins are not allowed"
    assert hal.setPinLow(1.5) == -1, "Non integer pins are not allowed"

def test_setPWM(hal):
    assert hal.setPWM(5, 128, 0) == (5, 128, 0), "Correct PWM parameters"
    assert hal.setPWM(5, 64, 1) == (5, 64, 1), "Correct PWM parameters"
    assert hal.setPWM(0, 64, 1) == -1, "Incorrect Pin (zero)"
    assert hal.setPWM(-1, 64, 1) == -1, "Incorrect Pin (negative)"
    assert hal.setPWM(3.2, 64, 1) == -1, "Incorrect Pin (non-integer)"
    assert hal.setPWM(5, 300, 5) == -1, "Incorrect duty cycle (out of range)"
    assert hal.setPWM(5, 0, 5) == -1, "Incorrect duty cycle (zero)"
    assert hal.setPWM(5, -8, 5) == -1, "Incorrect duty cycle (negative)"
    assert hal.setPWM(5, 7.3, 5) == -1, "Incorrect duty cycle (non integer)"
    assert hal.setPWM(5, 8, -1) == -1, "Incorrect frequency index (negative)"
    assert hal.setPWM(5, 8, 5.5) == -1, "Incorrect frequency index (non-integer)"
    assert hal.setPWM(5, 8, 20) == -1, "Incorrect frequency index (out of range)"

def test_setDirection(hal):
    assert hal.setDirection(0, 5) == (5, 0)
    assert hal.setDirection(1, 20) == (20, 1)
    assert hal.setDirection(2, 20) == -1, "Incorrect direction (non boolean)"
    assert hal.setDirection(-1, 20) == -1, "Incorrect direction (negative)"
    assert hal.setDirection(2.5, 20) == -1, "Incorrect direction (float)"
    assert hal.setDirection(1, 0) == -1, "Incorrect pin (zero)"
    assert hal.setDirection(1, -5) == -1, "Incorrect pin (negative)"
    assert hal.setDirection(0, 30) == -1, "Incorrect pin (out of range)"

def test_setDEMUX(hal):
    assert hal.selectDEMUX(0, 5, 6) == ((5, 0), (6, 0)), "pin0 low, pin1 low"
    assert hal.selectDEMUX(1, 5, 6) == ((5, 1), (6, 0)), "pin0 high, pin1 low"
    assert hal.selectDEMUX(2, 5, 6) == ((5, 0), (6, 1)), "pin0 low, pin1 high"
    assert hal.selectDEMUX(3, 5, 6) == ((5, 1), (6, 1)), "pin0 high, pin1 high"
    assert hal.selectDEMUX(4, 5, 6) == -1, "index out of range"
    assert hal.selectDEMUX(1, 0, 6) == -1, "pin0 out of range"
    assert hal.selectDEMUX(1, 5, 0) == -1, "pin1 out of range"

def test_moveStepperMotor(hal):
    freq_index = 3
    duty_cycle = 128
    step_pin = 4
    direction_pin0 = None
    direction0 = 0
    direction_pin1 = 10
    direction1 = 1
    assert hal.moveStepperMotor(step_pin, direction_pin0, direction0, duty_cycle, freq_index) == (None, (step_pin, duty_cycle, freq_index))
    assert hal.moveStepperMotor(step_pin, direction_pin1, direction1, duty_cycle, freq_index) == ((direction_pin1, direction1), (step_pin, duty_cycle, freq_index))
    assert hal.moveStepperMotor(-1, direction_pin0, direction0, duty_cycle, freq_index) == -1, "step pin out of range"
    assert hal.moveStepperMotor(step_pin, -1, direction0, duty_cycle, freq_index) == -1, "direction pin out of range"
    assert hal.moveStepperMotor(step_pin, direction_pin0, -1, duty_cycle, freq_index) == (None, (step_pin, duty_cycle, freq_index)), "direction val not boolean"
    assert hal.moveStepperMotor(step_pin, direction_pin0, direction0, -1, freq_index) == -1, "duty cycle out of range"
    assert hal.moveStepperMotor(step_pin, direction_pin0, direction0, duty_cycle, -1) == -1, "freq index out of range"

def test_stopStepperMotor(hal):
    assert hal.stopStepperMotor(5) == (5, 0)
    assert hal.stopStepperMotor(10) == (10, 0)
    assert hal.stopStepperMotor(30) == -1
    assert hal.stopStepperMotor(-1) == -1
    assert hal.stopStepperMotor(3.5) == -1

def test_checkLimitSwitch(hal):
    assert hal.checkLimitSwitch(0) == 0
    assert hal.checkLimitSwitch(1) == 1
    assert hal.checkLimitSwitch(2) == 0
    assert hal.checkLimitSwitch(3) == 1
    assert hal.checkLimitSwitch(4) == -1
    assert hal.checkLimitSwitch(-1) == -1





















