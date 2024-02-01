from wpilib import XboxController
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from drivetrain.drivetrainPhysical import MAX_FWD_REV_SPEED_MPS
from drivetrain.drivetrainPhysical import MAX_STRAFE_SPEED_MPS
from drivetrain.drivetrainPhysical import MAX_ROTATE_SPEED_RAD_PER_SEC
from drivetrain.drivetrainPhysical import MAX_ROTATE_ACCEL_RAD_PER_SEC_2
from drivetrain.drivetrainPhysical import MAX_TRANSLATE_ACCEL_MPS2
from utils.faults import Fault
from utils.signalLogging import log


class DriverInterface:
    """Class to gather input from the driver of the robot"""

    def __init__(self):
        ctrlIdx = 0
        self.ctrl = XboxController(ctrlIdx)
        self.connectedFault = Fault(f"Driver XBox Controller ({ctrlIdx}) Unplugged")
        self.intakeCmd = False
        self.ejectCmd = False
        self.autoAlignCmd = False

    def update(self):
        """Main update - call this once every 20ms"""
        if self.ctrl.isConnected():
            # Only attempt to read from the joystick if it's plugged in
            self.intakeCmd = self.ctrl.getLeftBumper()
            self.ejectCmd = self.ctrl.getBButton()
            self.autoAlignCmd = self.ctrl.getXButton()
            self.connectedFault.setNoFault()
        else:
            # If the joystick is unplugged, pick safe-state commands and raise a fault
            self.intakeCmd = False
            self.ejectCmd = False
            self.autoAlignCmd = False
            self.connectedFault.setFaulted()

        log("DI connected", self.ctrl.isConnected(), "bool")