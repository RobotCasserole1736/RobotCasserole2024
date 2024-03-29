from wpilib import PWMMotorController
from utils.constants import LED_BLOCK_CTRL_PWM, LED_STRIPS_CTRL_PWM
from utils.singleton import Singleton

class LEDControl(metaclass=Singleton):
    def __init__(self):
        # Put any one-time init code here
        # self.speakerAutoAlignActive = False
        # self.ampAutoAlignActive = False
        self.noteInIntake = False
        self._noteInIntakePrev = False
        self._noteInIntakeCounter = 0
        self.ctrlBlock = PWMMotorController("LEDBlockCtrl", LED_BLOCK_CTRL_PWM)
        self.ctrlStrips = PWMMotorController("LEDStripsCtrl", LED_STRIPS_CTRL_PWM)
        self.sampleTime = 0.1

    def update(self):
        if self.noteInIntake and not self._noteInIntakePrev:
            self._noteInIntakeCounter = int(
                3.0 / self.sampleTime
            )  # Set LED's to blink for 1 second
        if self._noteInIntakeCounter > 0:
            pwmVal = -0.35  # Green Blink
            self._noteInIntakeCounter -= 1
        elif self.noteInIntake:
            pwmVal = 0.35 # Solid Green
        else:
            pwmVal = 0.0  # default = off

        self.ctrlBlock.set(pwmVal)
        self.ctrlStrips.set(pwmVal)
        self._noteInIntakePrev = self.noteInIntake

    # def setSpeakerAutoAlignActive(self, isActive):
    #     self.speakerAutoAlignActive = isActive

    # def setAmpAutoAlignActive(self, isActive):
    #     self.ampAutoAlignActive = isActive

    def setNoteInIntake(self, hasNote):
        self.noteInIntake = hasNote
