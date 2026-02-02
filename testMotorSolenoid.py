import HAL_shell
from test_HardwareControls import SCodeParse, Solenoid, HAL
from pigpio_shell import pigpio_shell as pi
import pigpio
import csv
import time
import pytest
from numpy import heaviside as u

@pytest.fixture
def motorsolenoid():
    motorsolenoid = Solenoid(HAL(pi()))
    return motorsolenoid

@pytest.mark.parametrize("reservoir, exception", [
    (0, None),
    (1, None),
    (2, None),
    (3, None),
    (4, ValueError),
    (100, ValueError),
    (-10, ValueError),
    ('x', ValueError)
])
def test_setReservoirSelect(reservoir, exception, motorsolenoid):
    if exception is None:
        match reservoir:
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
        motorsolenoid.setReservoirSelect(reservoir)
        assert motorsolenoid.hal.pi.read(motorsolenoid.RESERVOIR_SELECT_LOWBIT)[0] == val0
        assert motorsolenoid.hal.pi.read(motorsolenoid.RESERVOIR_SELECT_HIGHBIT)[0] == val1
    else:
        with pytest.raises(exception):
            motorsolenoid.setReservoirSelect(reservoir)


@pytest.mark.parametrize("distance_value, axis, exception", [
    (10, 'X', None),
    (10, 'Y', None),
    (-10, 'X', None),
    (-10, 'Y', None),
    ('x', 'X', TypeError),
    ('y', 'Y', TypeError),
    (10, 1, ValueError),
    (10, -5, ValueError),
    (10, 'write', ValueError),
])
def test_moveMotor(distance_value, axis, exception, motorsolenoid):
    if exception is None:
        match axis:
            case 'X':
                step_pin = motorsolenoid.LOCOMOTIVE_STEP_PIN_X
            case 'Y':
                step_pin = motorsolenoid.LOCOMOTIVE_STEP_PIN_Y
        motorsolenoid.moveMotor(distance_value, axis)
        assert motorsolenoid.hal.pi.read(step_pin)[0] == motorsolenoid.DUTY_CYCLE_HALF
        assert motorsolenoid.hal.pi.read(step_pin)[1] == motorsolenoid.PWM_FREQUENCY_LIST[motorsolenoid.PWM_FREQUENCY_INDEX]
        assert motorsolenoid.time_value_s == abs(distance_value) / (motorsolenoid.STEP_MODE_VALUE * 
                            motorsolenoid.PWM_FREQUENCY_LIST[motorsolenoid.PWM_FREQUENCY_INDEX] * motorsolenoid.DISTANCE_PER_STEP)
    else:
        with pytest.raises(exception):
            motorsolenoid.moveMotor(distance_value, axis)


@pytest.mark.parametrize("exception", [(None)])
def test_pumpOn(exception, motorsolenoid):
    if exception is None:
        motorsolenoid.pumpOn()
        assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_STEP_PIN)[0] == motorsolenoid.DUTY_CYCLE_HALF
        assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_STEP_PIN)[1] == motorsolenoid.PWM_FREQUENCY_LIST[motorsolenoid.PWM_FREQUENCY_INDEX]
    else:
        with pytest.raises(exception):
            motorsolenoid.pumpOn()

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
def test_openAirValve(exception, motorsolenoid):
    if exception is None:
        motorsolenoid.openAirValve()
        assert motorsolenoid.hal.pi.read(motorsolenoid.AIR_VALVE_PIN)[0] == 255
    else:
        with pytest.raises(exception):
            motorsolenoid.openAirValve()

@pytest.mark.parametrize("exception", [None])
def test_closeAirValve(exception, motorsolenoid):
    if exception is None:
        motorsolenoid.openAirValve()
        motorsolenoid.closeAirValve()
        assert motorsolenoid.hal.pi.read(motorsolenoid.AIR_VALVE_PIN)[0] == 0
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
def test_pwmAirValve(pwm_val, exception, motorsolenoid):
    if exception is None:
        motorsolenoid.pwmAirValve(pwm_val)
        assert motorsolenoid.hal.pi.read(motorsolenoid.AIR_VALVE_PIN)[0] == pwm_val
        assert motorsolenoid.hal.pi.read(motorsolenoid.AIR_VALVE_PIN)[1] == motorsolenoid.PWM_FREQUENCY_LIST[motorsolenoid.VALVE_FREQUENCY_INDEX]
    else:
        with pytest.raises(exception):
            motorsolenoid.pwmAirValve(pwm_val)

def test_shutdown(motorsolenoid):
    motorsolenoid.moveMotor(10, 'X')
    motorsolenoid.openAirValve()
    motorsolenoid.pumpOn()
    motorsolenoid.shutdown()
    assert motorsolenoid.hal.pi.read(motorsolenoid.AIR_VALVE_PIN)[0] == 0
    assert motorsolenoid.hal.pi.read(motorsolenoid.PERISTALTIC_STEP_PIN)[0] == 0
    assert motorsolenoid.hal.pi.read(motorsolenoid.LOCOMOTIVE_STEP_PIN_X)[0] == 0
