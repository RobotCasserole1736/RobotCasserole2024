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
        # contoller 
        CtrlIdx = 0
        self.ctrl = XboxController(CtrlIdx)
        self.vXCmd = 0
        self.vYCmd = 0
        self.vRotCmd = 0
        
    def update(self):
        # value of contoller buttons
       
        if self.ctrl.isConnected:

            RawXJoyCmd = self.ctrl.getLeftX
            #offseason used Y axis for x command. Is that what we want to do?
            RawyJoyCmd = self.ctrl.getLeftY
        else:
            self.vXCmd = 0
            self.vYCmd = 0
            self.vRotCmd = 0



    def getVyCmd(self):
        return self.vYCmd
        

    def getVrotCmd(self):
        return self.vRotCmd

    def getliftlowerCmd(self):
        # returnself. lift lower comand
        pass

    def getAutodrivetoampCmd(self):
        # returnself. go to amp comand
        pass

    def getAutodrivetoclimbCmd(self):
        # returnself. go to climb command
        pass

