from wrappers.wrapperedSparkMax import WrapperedSparkMax
from utils.calibration import Calibration

class SimpleIntake():
    def __init__(self):
        self.ctrl1 = WrapperedSparkMax(10, "Intake Motor 1")
        self.ctrl2 = WrapperedSparkMax(11, "Intake Motor 2")
        self.intakeCmd = False
        self.ejectCmd = False
        self.intakeSpdCal = Calibration("Intake", 7.0, "V", 0.0, 13.0)
        self.ejectSpdCal  = Calibration("Eject", 7.0, "V", 0.0, 13.0)

    def setCmd(self, intakeCommanded, ejectCommanded):
        self.intakeCmd = intakeCommanded
        self.ejectCmd  = ejectCommanded

    def update(self):
        spdCmd = 0.0 # Default
        if(self.intakeCmd):
            spdCmd = self.intakeSpdCal.get()
        elif(self.ejectCmd):
            spdCmd = -1.0 * self.ejectSpdCal.get()

        self.ctrl1.setVoltage(spdCmd)
        self.ctrl2.setVoltage(-1.0 * spdCmd)
