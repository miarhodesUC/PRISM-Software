import pigpio 

class Solenoid():
    def __init__(self, pin):
        self.pi=pigpio.pi()
        self.pin = pin
    def closeSolenoid(self):
        self.pi.write(self.pin, 1)
    def openSolenoid(self):
        self.pi.write(self.pin, 0)
    def modulateSolenoid(self, dutyCycle=0.5):
        self.pi.set_PWM_dutycycle(self.pin, dutyCycle)

class StepperMotor():
    def __init__(self):
        self.pi=pigpio.pi()
        # Set pins for each wire of the motor driver
    


