# testFirmware2
import numpy as np
import time
import pytest
from Firmware import HAL
from numpy import heaviside as u
from pigpio_shell import pigpio_shell

@pytest.fixture
def hal():
    hal = HAL(pigpio_shell())
    return hal

@pytest.mark.parametrize('pin, expected, exception', [
    (4, [255, 0], None),
    (3, [255, 0], None),
    (-1, None, ValueError),
    (35, None, ValueError),
    (1.5, None, TypeError)])
def test_setPinHigh(hal, pin, expected, exception):
    if exception is None:
        hal.setPinHigh(pin)
        assert np.array_equal(hal.pi.read(pin), expected)
    else:
        with pytest.raises(exception):
            hal.setPinHigh(pin)

@pytest.mark.parametrize('pin, expected, exception', [
    (4, [0, 0], None),
    (3, [0, 0], None),
    (-1, None, ValueError),
    (35, None, ValueError),
    (1.5, None, TypeError)])

def test_setPinLow(hal, pin, expected, exception):
    if exception is None:
        hal.setPinLow(pin)
        assert np.array_equal(hal.pi.read(pin), expected)
    else:
        with pytest.raises(exception):
            hal.setPinHigh(pin)
@pytest.mark.parametrize("pin, dutycycle, frequency_index, exception", [
    (10, 128, 3, None),
    (1, 1, 0, None),
    (22, 255, 17, None),
    (2.5, 8, 8, TypeError),
    (-1, 8, 8, ValueError),
    (3, 0.75, 8, TypeError),
    (3, -4, 8, ValueError),
    (3, 300, 8, ValueError),
    (10, 128, 3.5, TypeError),
    (10, 128, -3, ValueError),
    (10, 128, 20, ValueError),
])
def test_setPWM(hal, pin, dutycycle, frequency_index, exception):
    if exception is None:
        hal.setPWM(pin, dutycycle, frequency_index)
        assert np.array_equal(hal.pi.read(pin), [dutycycle, hal.pi.freq_ref[frequency_index]])
    else:
        with pytest.raises(exception):
            hal.setPWM(pin, dutycycle, frequency_index)

@pytest.mark.parametrize('direction, pin, expected, exception', [
    (1, 4, 255, None),
    (0, 5, 0, None),
    (-1, 19, 0, ValueError),
    (0.5, 10, 0, ValueError),
    (5, 4, 0, ValueError),
    (1, 5.5, 255, TypeError),
    (1, 50, 255, ValueError)
])
def test_setDirection(hal, direction, pin, expected, exception):
    if exception is None:
        hal.setDirection(direction, pin)
        assert np.array_equal(hal.pi.read(pin), [expected, 0])
    else:
        with pytest.raises(exception):
            hal.setDirection(direction, pin)

@pytest.mark.parametrize("selection_index, pin0, pin1, exception", [
    (0, 10, 11, None),
    (1, 10, 11, None),
    (2, 10, 11, None),
    (3, 10, 11, None),
    (-1, 10, 11, ValueError),
    (0.5, 10, 11, ValueError),
    (5, 10, 11, ValueError),
    (0, 50, 50, ValueError),
    (0, 0.5, 0.5, ValueError)
])
def test_selectDEMUX(hal, selection_index, pin0, pin1, exception):
    if exception is None:
        hal.selectDEMUX(selection_index, pin0, pin1)
        match selection_index:
            case 0:
                assert hal.pi.read(pin0)[0] == 0
                assert hal.pi.read(pin1)[0] == 0
            case 1:
                assert hal.pi.read(pin0)[0] == 255
                assert hal.pi.read(pin1)[0] == 0
            case 2:
                assert hal.pi.read(pin0)[0] == 0
                assert hal.pi.read(pin1)[0] == 255
            case 3:
                assert hal.pi.read(pin0)[0] == 255
                assert hal.pi.read(pin1)[0] == 255
    else:
        with pytest.raises(exception):
            hal.selectDEMUX(selection_index, pin0, pin1)
@pytest.mark.parametrize("step_pin, direction_pin, direction, duty_cycle, frequency_index, exception", [
    (5, None, None, 128, 5, None),
    (5, 18, 1, 128, 5, None),
    (10, 1, 0, 64, 17, None),
    (-5, None, None, 128, 5, ValueError),
    (0.5, None, None, 128, 5, TypeError),
    (500, None, None, 128, 5, ValueError),
    (5, 7, 5, 5, 5, ValueError),
    (10, 22, -1, 10, 5, ValueError),
    (10, 22, 0, 300, 5, ValueError),
    (10, None, None, 128, 20, ValueError)
])
def test_moveStepperMotor(step_pin, direction_pin, direction, duty_cycle, frequency_index, exception, hal):
    if exception is None:
        hal.moveStepperMotor(step_pin, direction_pin, direction, duty_cycle, frequency_index)
        assert hal.pi.read(step_pin)[0] == duty_cycle
        assert hal.pi.read(step_pin)[1] == hal.pi.freq_ref[frequency_index]
        if direction is not None:
            assert hal.pi.read(direction_pin)[0] == direction * 255
    else:
        with pytest.raises(exception):
            hal.moveStepperMotor(step_pin, direction_pin, direction, duty_cycle, frequency_index)


