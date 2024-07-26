from drivetrain.drivetrainCommand import DrivetrainCommand
from drivetrain.drivetrainPhysical import MAX_FWD_REV_SPEED_MPS,MAX_STRAFE_SPEED_MPS,\
MAX_ROTATE_SPEED_RAD_PER_SEC,MAX_TRANSLATE_ACCEL_MPS2,MAX_ROTATE_ACCEL_RAD_PER_SEC_2
from pieceHandling.gamepieceHandling import GamePieceHandling
from utils.allianceTransformUtils import onRed
from utils.faults import Fault
from utils.signalLogging import log
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpilib import XboxController

class DriverInterface:
    """Class to gather input from the driver of the robot"""

    def __init__(self):
        # contoller
        ctrlIdx = 0
        self.ctrl = XboxController(ctrlIdx)
        self.velXCmd = 0
        self.velYCmd = 0
        self.velTCmd = 0
        self.velWinchCmdDown = 0.0 # 0-1 value mapped to 12 volts
        self.velWinchCmdUp = False
        self.allowWinchCmd = False
        self.gyroResetCmd = False
        self.connectedFault = Fault(f"Driver XBox Controller ({ctrlIdx}) Unplugged")
        self.velXSlewRateLimiter = SlewRateLimiter(rateLimit=MAX_TRANSLATE_ACCEL_MPS2)
        self.velYSlewRateLimiter = SlewRateLimiter(rateLimit=MAX_TRANSLATE_ACCEL_MPS2)
        self.velTSlewRateLimiter = SlewRateLimiter(rateLimit=MAX_ROTATE_ACCEL_RAD_PER_SEC_2)

    def update(self):
        # value of contoller buttons

        if self.ctrl.isConnected():
            # Convert from  joystic sign/axis conventions to robot velocity conventions
            vXJoyRaw = self.ctrl.getLeftY() * -1
            vYJoyRaw = self.ctrl.getLeftX() * -1
            vRotJoyRaw = self.ctrl.getRightX() * -1

            # Correct for alliance
            if onRed():
                vXJoyRaw *= -1.0
                vYJoyRaw *= -1.0

            # deadband
            vXJoyWithDeadband = applyDeadband(vXJoyRaw, 0.15)
            vYJoyWithDeadband = applyDeadband(vYJoyRaw, 0.15)
            vRotJoyWithDeadband = applyDeadband(vRotJoyRaw, 0.2)

            slowMult = 1.0 if (self.ctrl.getRightBumper()) else 0.75

            # velocity cmd
            velCmdXRaw = vXJoyWithDeadband * MAX_STRAFE_SPEED_MPS * slowMult
            velCmdYRaw = vYJoyWithDeadband * MAX_FWD_REV_SPEED_MPS * slowMult
            velCmdRotRaw = vRotJoyWithDeadband * MAX_ROTATE_SPEED_RAD_PER_SEC

            # Slew rate limiter
            self.velXCmd = self.velXSlewRateLimiter.calculate(velCmdXRaw)
            self.velYCmd = self.velYSlewRateLimiter.calculate(velCmdYRaw)
            self.velTCmd = self.velTSlewRateLimiter.calculate(velCmdRotRaw) 

            # Climber Winch Cmd
            self.velWinchCmdUp = applyDeadband(self.ctrl.getRightTriggerAxis(),0.1) * -12.0
            self.velWinchCmdDown = applyDeadband(self.ctrl.getLeftTriggerAxis(),0.1) * 12.0
            self.allowWinchCmd = self.ctrl.getLeftBumper()

            self.gyroResetCmd = self.ctrl.getAButtonPressed()

            self.connectedFault.setNoFault()

            if GamePieceHandling().getHasGamePiece():
                self.ctrl.setRumble(self.ctrl.RumbleType.kBothRumble,0.15)
            else:
                self.ctrl.setRumble(self.ctrl.RumbleType.kBothRumble,0)

        else:
            # If the joystick is unplugged, pick safe-state commands and raise a fault
            self.velWinchCmd = 0.0
            self.velXCmd = 0.0
            self.velYCmd = 0.0
            self.velTCmd = 0.0
            self.gyroResetCmd = False
            self.connectedFault.setFaulted()

        log("DI FwdRev Cmd", self.velXCmd, "mps")
        log("DI Strafe Cmd", self.velYCmd, "mps")
        log("DI Rot Cmd", self.velTCmd, "radps")
        log("DI connective fault", self.ctrl.isConnected(), "bool")
        log("DI gyroResetCmd", self.gyroResetCmd, "bool")
        log("DI velWinchCmdDown", self.velWinchCmdDown, "V")
        log("DI velWinchCmdUp", self.velWinchCmdUp, "Bool")

    def getCmd(self):
        retval = DrivetrainCommand()
        retval.velX = self.velXCmd
        retval.velY = self.velYCmd
        retval.velT = self.velTCmd
        return retval

    def getWinchCmd(self):
        if self.allowWinchCmd:
            if not self.velWinchCmdDown == 0 and not self.velWinchCmdUp:
                return self.velWinchCmdDown
            elif self.velWinchCmdUp and self.velWinchCmdDown == 0:
                return self.velWinchCmdUp
            else:
                return 0
        else:
            return 0

    def getGyroResetCmd(self):
        return self.gyroResetCmd
