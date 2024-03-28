from wpilib import PWMMotorController
from utils.constants import LED_CTRL_PWM
from utils.singleton import Singleton

class LEDControl(metaclass=Singleton):
    def __init__(self):
        # Put any one-time init code here
        # self.speakerAutoAlignActive = False
        # self.ampAutoAlignActive = False
        self.noteInIntake = False
        self._noteInIntakePrev = False
        self._noteInIntakeCounter = 0
        self.ctrl = PWMMotorController("LEDCtrl", LED_CTRL_PWM)
        self.sampleTime = 0.1

    def update(self):
        if self.noteInIntake and not self._noteInIntakePrev:
            self._noteInIntakeCounter = int(
                1.0 / self.sampleTime
            )  # Set LED's to blink for 1 second
        if self._noteInIntakeCounter > 0:
            pwmVal = -0.35  # Green Blink
            self._noteInIntakeCounter -= 1
        else:
            pwmVal = 0.0  # default = off

        self.ctrl.set(pwmVal)
        self._noteInIntakePrev = self.noteInIntake

    # def setSpeakerAutoAlignActive(self, isActive):
    #     self.speakerAutoAlignActive = isActive

    # def setAmpAutoAlignActive(self, isActive):
    #     self.ampAutoAlignActive = isActive

    def setNoteInIntake(self, hasNote):
        self.noteInIntake = hasNote
