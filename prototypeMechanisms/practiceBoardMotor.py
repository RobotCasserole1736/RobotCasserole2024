from wrappers.wrapperedSparkMax import WrapperedSparkMax
from utils.calibration import Calibration

class PracticeBoardMotor():
    def __init__(self):
        self.ctrl1 = WrapperedSparkMax(10, "Shooter Motor 1")
        self.forwardCmd = False
        self.backwardCmd = False
        self.speedSpdCal = Calibration("Shoot", 5.0, "V", 0.0, 13.0)

    def setCmd(self, forwardCmd, backwardCmd):
        self.forwardCmd = forwardCmd
        self.backwardCmd = backwardCmd

    def update(self):
        spdCmd = 0.0 # Default
        if self.forwardCmd:
            spdCmd = self.speedSpdCal.get()
        elif self.backwardCmd:
            spdCmd = -self.speedSpdCal.get()

        self.ctrl1.setVoltage(spdCmd)