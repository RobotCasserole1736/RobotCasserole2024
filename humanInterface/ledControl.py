from wpilib import PWMMotorController
from utils.singleton import Singleton

class LEDControl(metaclass=Singleton):
    def __init__(self):
        # Put any one-time init code here
        self.speakerAutoAlignActive = False
        self.ampAutoAlignActive = False
        self.noteInIntake = False
        self._noteInIntakePrev = False
        self._noteInIntakeCounter = 0
        self.ctrl = PWMMotorController("LEDCtrl", 9)
        self.sampleTime = 0.1

    def update(self):
        pwmVal = 0.0  # default = off

        if self.noteInIntake and not self._noteInIntakePrev:
            self._noteInIntakeCounter = int(
                1.0 / self.sampleTime
            )  # Set LED's to blink for 1 second

        if self.speakerAutoAlignActive:
            pwmVal = 0.5  # Blue Solid
        elif self.setAmpAutoAlignActive:
            pwmVal = 0.25 # Want to be red, but no idea what to put for pwm
        elif self._noteInIntakeCounter > 0:
            pwmVal = -0.35  # Green Blink
            self._noteInIntakeCounter -= 1

        self.ctrl.set(pwmVal)
        self._noteInIntakePrev = self.noteInIntake

    def setSpeakerAutoAlignActive(self, isActive):
        self.speakerAutoAlignActive = isActive

    def setAmpAutoAlignActive(self, isActive):
        self.ampAutoAlignActive = isActive

    def setNoteInIntake(self, hasNote):
        self.noteInIntake = hasNote
