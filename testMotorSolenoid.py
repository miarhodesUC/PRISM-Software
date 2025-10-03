import HAL_shell
from HardwareControls import SCodeParse, MotorSolenoid, HAL
from pigpio_shell import pigpio_shell as pi
import pigpio
import csv
import time
import pytest
from numpy import heaviside as u

@pytest.fixture
def motorsolenoid():
    motorsolenoid = MotorSolenoid(HAL())
    return motorsolenoid

@pytest.mark.parametrize("axis, exception", [
    (0, None),
    (1, None),
    (2, None),
    (3, None),
    (4, ValueError),
    (100, ValueError),
    (-10, ValueError),
    ('x', ValueError)
])
def test_setLocomotiveSelect(axis, exception, motorsolenoid):
    if exception is None:
        match axis:
            case 0:
                val0 = 0
                val1 = 0
            case 1:
                val0 = 255
                val1 = 0
            case 2:
                val0 = 0
                val1 = 255
            case 3:
                val0 = 255
                val1 = 255
        motorsolenoid.setLocomotiveSelect(axis)
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_SELECT_LOWBIT)[0] == val0
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_SELECT_HIGHBIT)[0] == val1
    else:
        with pytest.raises(exception):
            motorsolenoid.setLocomotiveSelect(axis)

@pytest.mark.parametrize("pump, exception", [
    (0, None),
    (1, None),
    (2, None),
    (3, None),
    (4, ValueError),
    (100, ValueError),
    (-10, ValueError),
    ('x', ValueError)
])
def test_setPeristalticSelect(pump, exception, motorsolenoid):
    if exception is None:
        match pump:
            case 0:
                val0 = 0
                val1 = 0
            case 1:
                val0 = 255
                val1 = 0
            case 2:
                val0 = 0
                val1 = 255
            case 3:
                val0 = 255
                val1 = 255
        motorsolenoid.setPeristalticSelect(pump)
        assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_SELECT_LOWBIT)[0] == val0
        assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_SELECT_HIGHBIT)[0] == val1
    else:
        with pytest.raises(exception):
            motorsolenoid.setPeristalticSelect(pump)

@pytest.mark.parametrize("distance_value, axis, exception", [
    (10, 'X', None),
    (10, 'Y', None),
    (10, 'T', None),
    (10, 'IDLE', None),
    (-10, 'X', None),
    (-10, 'Y', None),
    (-10, 'T', None),
    (-10, 'IDLE', None),
    ('x', 'X', TypeError),
    ('y', 'Y', TypeError),
    ('t', 'T', TypeError),
    (10, 1, ValueError),
    (10, -5, ValueError),
    (10, 'write', ValueError),
])
def test_moveMotor(distance_value, axis, exception, motorsolenoid):
    if exception is None:
        motorsolenoid.moveMotor(distance_value, axis)
        match axis:
            case 'X':
                val0 = 255
                val1 = 0
            case 'Y':
                val0 = 0
                val1 = 255
            case 'T':
                val0 = 255
                val1 = 255
            case 'IDLE':
                val0 = 0
                val1 = 0
        motorsolenoid.moveMotor(distance_value, axis)
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_SELECT_LOWBIT)[0] == val0
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_SELECT_HIGHBIT)[0] == val1
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_STEP_PIN)[0] == motorsolenoid.DUTY_CYCLE_HALF
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_STEP_PIN)[1] == motorsolenoid.PWM_FREQUENCY_LIST[motorsolenoid.PWM_FREQUENCY_INDEX]
        time.sleep(2)
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_STEP_PIN)[0] == 0
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_STEP_PIN)[1] == 0
    else:
        with pytest.raises(exception):
            motorsolenoid.moveMotor(distance_value, axis)

@pytest.mark.parametrize("axis, exception", [
    # Testing ALL and T case will be done by inspection
    ('X', None),
    ('Y', None),
    (1, ValueError),
    (-1, ValueError),
    ('Z', ValueError),
    (1.6, ValueError)
])
def test_homeMotor(axis, exception, motorsolenoid):
    if exception is None:
        motorsolenoid.homeMotor(axis)
        match axis:
            case 'X':
                val0 = 255
                val1 = 0
            case 'Y':
                val0 = 0
                val1 = 255
            case 'T':
                val0 = 255
                val1 = 255
            case 'IDLE':
                val0 = 0
                val1 = 0
        motorsolenoid.homeMotor(axis)
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_SELECT_LOWBIT)[0] == val0
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_SELECT_HIGHBIT)[0] == val1
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_STEP_PIN)[0] == motorsolenoid.DUTY_CYCLE_HALF
        assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_STEP_PIN)[1] == motorsolenoid.PWM_FREQUENCY_LIST[motorsolenoid.PWM_FREQUENCY_INDEX]
    else:
        with pytest.raises(exception):
            motorsolenoid.homeMotor(axis)

@pytest.mark.parametrize("pump, exception", [
    (0, None),
    (1, None),
    (2, None),
    (3, None),
    (4, ValueError),
    (-1, ValueError),
    ('0', TypeError)
])
def test_pumpOn(pump, exception, motorsolenoid):
    if exception is None:
        motorsolenoid.pumpOn(pump)
        match pump:
            case 0:
                val0 = 0
                val1 = 0
            case 1:
                val0 = 255
                val1 = 0
            case 2:
                val0 = 0
                val1 = 255
            case 3:
                val0 = 255
                val1 = 255
        motorsolenoid.setPeristalticSelect(pump)
        assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_SELECT_LOWBIT)[0] == val0
        assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_SELECT_HIGHBIT)[0] == val1
        assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_STEP_PIN)[0] == motorsolenoid.DUTY_CYCLE_HALF
        assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_STEP_PIN)[1] == motorsolenoid.PWM_FREQUENCY_LIST[motorsolenoid.VALVE_FREQUENCY_INDEX]
    else:
        with pytest.raises(exception):
            motorsolenoid.setPeristalticSelect(pump)

@pytest.mark.parametrize("exception", [(None)])
def test_pumpOff(exception, motorsolenoid):
    if exception is None:
        motorsolenoid.pumpOff()
        assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_STEP_PIN)[0] == 0
        assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_STEP_PIN)[1] == 0
    else:
        with pytest.raises(exception):
            motorsolenoid.pumpOff()

@pytest.mark.parametrize("exception", [None])
def test_openValve(exception, motorsolenoid):
    if exception is None:
        motorsolenoid.openValve()
        assert motorsolenoid.hal.pi.read(motorsolenoid.SOLENOID_PIN)[0] == 255
    else:
        with pytest.raises(exception):
            motorsolenoid.openValve()

@pytest.mark.parametrize("exception", [None])
def test_closeValve(exception, motorsolenoid):
    if exception is None:
        motorsolenoid.openValve()
        motorsolenoid.closeValve()
        assert motorsolenoid.hal.pi.read(motorsolenoid.SOLENOID_PIN)[0] == 0
    else:
        with pytest.raises(exception):
            pass

@pytest.mark.parametrize("pwm_val, exception", [
    (1, None),
    (32, None),
    (64, None),
    (128, None),
    (300, ValueError),
    ('200', TypeError),
    (-10, ValueError)
])
def test_pwmValve(pwm_val, exception, motorsolenoid):
    if exception is None:
        motorsolenoid.pwmValve(pwm_val)
        assert motorsolenoid.hal.pi.read(motorsolenoid.SOLENOID_PIN)[0] == pwm_val
        assert motorsolenoid.hal.pi.read(motorsolenoid.SOLENOID_PIN)[1] == motorsolenoid.PWM_FREQUENCY_LIST[motorsolenoid.PWM_FREQUENCY_INDEX]
    else:
        with pytest.raises(exception):
            motorsolenoid.pwmValve(pwm_val)