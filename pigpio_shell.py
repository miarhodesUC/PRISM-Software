
import numpy as np

class pigpio_shell():
    PIN_ARRAY = np.zeros((31, 2))
    PWM_FREQUENCY_LIST = [10, 20, 40, 50, 80, 100, 160, 200, 250, 320, 400, 500, 800, 1000, 1600, 2000, 4000, 8000]
    def __init__(self):
        self.pinout = self.PIN_ARRAY
        self.freq_ref = self.PWM_FREQUENCY_LIST
    def set_mode(x, y, z):
        return x, y, z
    def write(self, pin, state_bool):
        if type(pin) is not int:
            raise TypeError("Error in write: pin {} invalid, must be int".format(pin))
        if pin < 0:
            raise ValueError("Error in write: pin {} invalid, must be in range [0, 31]".format(pin))
        if pin > 31:
            raise ValueError("Error in write: pin {} invalid, must be in range [0, 31]".format(pin))
        if state_bool == 0:
            state = np.array([0, 0])
        elif state_bool == 1:
            state = np.array([255, 0])
        else:
            raise ValueError("Error in write: state_bool {} invalid, must be 0 or 1".format(state_bool))
        print("Set pin {0} to {1}".format(pin, state))
        self.pinout[pin] = state
        return state
    def read(self, pin):
        if type(pin) is not int:
            raise TypeError("Error in read: pin {} invalid, must be int".format(pin))
        if pin < 0:
            raise ValueError("Error in read: pin {} invalid, must be in range [0, 31]".format(pin))
        if pin > 31:
            raise ValueError("Error in read: pin {} invalid, must be in range [0, 31]".format(pin))
        state = self.pinout[pin]
        print("Read pin {0} with state {1}".format(pin, state))
        return state
    def set_PWM_frequency(self, pin, frequency):
        if type(pin) is not int:
            raise TypeError("Error in pwm: pin {} invalid, must be int".format(pin))
        if pin < 0:
            raise ValueError("Error in pwm: pin {} invalid, must be in range [0, 31]".format(pin))
        if pin > 31:
            raise ValueError("Error in pwm: pin {} invalid, must be in range [0, 31]".format(pin))
        if frequency < 0:
            raise ValueError("Error in set_PWM_frequency: frequency {} is invalid, must be in range [0, 10000]".format(frequency))
        if frequency > 10000:
            raise ValueError("Error in set_PWM_frequency: frequency {} is invalid, must be in range [0, 10000]".format(frequency))
        if type(frequency) is not int:
            raise TypeError("Error in set_PWM_frequency: frequency {} invalid, must be integer".format(frequency))
        print("Set pin {0} to frequency {1}".format(pin, frequency))
        self.pinout[pin][1] = frequency
        return frequency
    def set_PWM_dutycycle(self, pin, duty_cycle):
        if type(pin) is not int:
            raise TypeError("Error in duty: pin {} invalid, must be int".format(pin))
        if pin < 0:
            raise ValueError("Error in duty: pin {} invalid, must be in range [0, 31]".format(pin))
        if pin > 31:
            raise ValueError("Error in duty: pin {} invalid, must be in range [0, 31]".format(pin))
        if duty_cycle < 0:
            raise ValueError("Error in set_PWM_dutycycle: dutycycle {} is invalid, must be in range [0, 255]".format(duty_cycle))
        if duty_cycle > 255:
            raise ValueError("Error in set_PWM_dutycycle: dutycycle {} is invalid, must be in range [0, 255]".format(duty_cycle))
        if type(duty_cycle) is not int:
            raise TypeError("Error in set_PWM_dutycycle: dutycycle {} invalid, must be integer".format(duty_cycle))
        print("Set pin {0} to frequency {1}".format(pin, duty_cycle))
        self.pinout[pin][0] = duty_cycle
        return duty_cycle
