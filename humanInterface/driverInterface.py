from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from wpilib import XboxController
from drivetrain.drivetrainCommand import DrivetrainCommand
from drivetrain.drivetrainPhysical import MAX_FWD_REV_SPEED_MPS
from drivetrain.drivetrainPhysical import MAX_STRAFE_SPEED_MPS
from drivetrain.drivetrainPhysical import MAX_ROTATE_SPEED_RAD_PER_SEC
from drivetrain.drivetrainPhysical import MAX_TRANSLATE_ACCEL_MPS2
from drivetrain.drivetrainPhysical import MAX_ROTATE_ACCEL_RAD_PER_SEC_2
from drivetrain.controlStrategies.autoDrive import AutoDrive
from pieceHandling.gamepieceHandling import GamePieceHandling
from utils.faults import Fault
from utils.signalLogging import log
from utils.allianceTransformUtils import onRed

class DriverInterface:
    """Class to gather input from the driver of the robot"""

    def __init__(self):
        # contoller
        ctrlIdx = 0
        self.ctrl = XboxController(ctrlIdx)
        self.velXCmd = 0
        self.velYCmd = 0
        self.velTCmd = 0
        self.velWinchCmd = 0 
        self.gyroResetCmd = False
        self.connectedFault = Fault(f"Driver XBox Controller ({ctrlIdx}) Unplugged")

        self.velXSlewRateLimiter = SlewRateLimiter(rateLimit=MAX_TRANSLATE_ACCEL_MPS2)
        self.velYSlewRateLimiter = SlewRateLimiter(rateLimit=MAX_TRANSLATE_ACCEL_MPS2)
        self.velTSlewRateLimiter = SlewRateLimiter(
            rateLimit=MAX_ROTATE_ACCEL_RAD_PER_SEC_2
        )
        self.autoDrive = AutoDrive()
        #Currently using the driver controller to call autoDrive. Change this to operator controller later.
        

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
            
            # Set rachet command
            # TODO: is this needed? Can it be deleted?
            # if self.ctrl.getStartButton() == 1 and self.ctrl.getBackButton() == 0:
            # self.RachetCmd = 1
            # elif self.ctrl.getBackButton() == 0 and self.ctrl.getBackButton() == 1:
            # self.RachetCmd = 0
 

            # Climber Winch Cmd
            self.velWinchCmd = (
                #TODO - this command logic doesn't make sense. I believe drivers need to be able to control the winch in both directions. We also likely want a lock-out button so it isn't accidentally run during the match
                self.ctrl.getLeftTriggerAxis() + self.ctrl.getRightTriggerAxis()
            )

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
        #TODO - at the moment, velWinchCmdd is definitely not a bool...
        log("DI velWinchCmdd", self.velWinchCmd, "bool")

    # TODO - are these individual getters for x/y/theta needed?
    def getVxCmd(self):
        return self.velXCmd

    def getVyCmd(self):
        return self.velYCmd

    def getVrotCmd(self):
        return self.velTCmd

    def getCmd(self):
        retval = DrivetrainCommand()
        retval.velX = self.getVxCmd()
        retval.velY = self.getVyCmd()
        retval.velT = self.getVrotCmd()
        return retval

    def getliftlowerCmd(self):
        # returnself. lift lower comand
        pass

    def getAutodrivetoampCmd(self):
        # returnself. go to amp comand
        pass

    def getAutodrivetoclimbCmd(self):
        # returnself. go to climb command
        pass

    def getGyroResetCmd(self):
        return self.gyroResetCmd
