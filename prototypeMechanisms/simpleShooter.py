from wrappers.wrapperedSparkMax import WrapperedSparkMax
from utils.calibration import Calibration

class SimpleShooter():
    def __init__(self):
        self.ctrl1 = WrapperedSparkMax(13, "Shooter Motor 1")
        self.ctrl2 = WrapperedSparkMax(14, "Shooter Motor 2")
        self.shootCmd = False
        self.speedSpdCal = Calibration("Shoot", 7.0, "V", 0.0, 13.0)

    def setCmd(self, shootCmd):
        self.shootCmd = shootCmd

    def update(self):
        spdCmd = 0.0 # Default
        if(self.shootCmd):
            spdCmd = self.speedSpdCal.get()

        self.ctrl1.setVoltage(spdCmd)
        self.ctrl2.setVoltage(-1.0 * spdCmd)
