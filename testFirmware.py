# test file
from HardwareControls import SCodeParse, MotorSolenoid, I2C
import pytest

class MotorSolenoidShell():
    def __init__(self):
        print("Initializing motor-solenoid shell")
    def openValve(self):
        print("Opened valve")
    def closeValve(self):
        print("Closed valve")
    def pwmValve(self, pwm_value):
        print("PWM modulating valve at value {}".format(pwm_value))
    def homeMotorX(self):
        print("Homing motor X")
    def homeMotorY(self):
        print("Homing motor Y")
    def homeMotorT(self):
        print("Homing motor T")
    def moveMotorX(self, distance_value):
        print("Moving motor X {} units".format(distance_value))
    def moveMotorY(self, distance_value):
        print("Moving motor Y {} units".format(distance_value))
    def moveMotorT(self, distance_value):
        print("Moving motor T {} units".format(distance_value))
        
