from wpilib import XboxController
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from drivetrain.drivetrainCommand import DrivetrainCommand
from drivetrain.drivetrainPhysical import MAX_FWD_REV_SPEED_MPS
from drivetrain.drivetrainPhysical import MAX_STRAFE_SPEED_MPS
from drivetrain.drivetrainPhysical import MAX_ROTATE_SPEED_RAD_PER_SEC
from utils.faults import Fault
from utils.signalLogging import log
from utils.allianceTransformUtils import onRed
from utils.constants import WINCH_MAX_SPEED
from utils.constants import WINCH_MAX_ACCEL
from humanInterface.autoAlign import AutoAlign


class driverInterface:
    """Class to gather input from the driver of the robot"""

    def __init__(self):
        # contoller 
        ctrlIdx = 0
        self.ctrl = XboxController(ctrlIdx)
        self.velXCmd = 0
        self.velYCmd = 0
        self.velTCmd = 0
        self.WinchCmd = 0
        self.gyroResetCmd = False
        self.connectedFault = Fault(f"Driver XBox Controller ({ctrlIdx}) Unplugged")

        self.velWinchSlewRateLimiter = SlewRateLimiter(rateLimit=WINCH_MAX_ACCEL)
        self.velXSlewRateLimiter = SlewRateLimiter(rateLimit=MAX_TRANSLATE_ACCEL_MPS2)
        self.velYSlewRateLimiter = SlewRateLimiter(rateLimit=MAX_TRANSLATE_ACCEL_MPS2)
        self.velTSlewRateLimiter = SlewRateLimiter(
            rateLimit=MAX_ROTATE_ACCEL_RAD_PER_SEC_2
        )

    def update(self):
        # value of contoller buttons

        if self.ctrl.isConnected():
            vXJoyRaw = self.ctrl.getLeftY() * -1
            vYJoyRaw = self.ctrl.getLeftX() * -1
            vRotJoyRaw = self.ctrl.getRightX() * -1
   
            #deadband
            vXJoy = applyDeadband(vXJoyRaw,0.15)
            vYJoy = applyDeadband(vYJoyRaw,0.15)
            vRotJoy = applyDeadband(vRotJoyRaw,0.15)

            slowMult = .5 if (self.ctrl.getRightBumper()) else 1.0

            #velocity cmd
            velCmdXRaw = vXJoy * MAX_STRAFE_SPEED_MPS * slowMult
            velCmdYRaw = vYJoy * MAX_FWD_REV_SPEED_MPS * slowMult
            velCmdRotRaw = vRotJoy * MAX_ROTATE_SPEED_RAD_PER_SEC
            
            # Convert from  joystic sign/axis conventions to robot velocity conventions
            vXJoyRaw = -1.0 * self.ctrl.getLeftY()
            vYJoyRaw = -1.0 * self.ctrl.getLeftX()
            vTJoyRaw = -1.0 * self.ctrl.getRightX()

            # Set command for Climbing via left bumper
            WinchRawUp = self.ctrl.getLeftTriggerAxis()
            WinchRawDown = self.ctrl.getRightTriggerAxis()
            # Set rachet command

                #if self.ctrl.getStartButton() == 1 and self.ctrl.getBackButton() == 0:
                    #self.RachetCmd = 1
                #elif self.ctrl.getBackButton() == 0 and self.ctrl.getBackButton() == 1:
                    #self.RachetCmd = 0
                
            # Apply deadband to make sure letting go of the joystick actually stops the bot
            vXJoy = applyDeadband(vXJoyRaw, 0.15)
            vYJoy = applyDeadband(vYJoyRaw, 0.15)
            vTJoy = applyDeadband(vTJoyRaw, 0.15)

            # Slew rate limiter
            self.vXCmd = self.vXSlewRateLimiter.calculate(velCmdXRaw)
            self.vYCmd = self.vYSlewRateLimiter.calculate(velCmdYRaw)
            self.vRotCmd = self.vRotSlewRateLimiter.calculate(velCmdRotRaw)
        

            self.gyroResetCmd = self.ctrl.getAButtonPressed()

            self.connectedfault.setNoFault()


        else:
            # If the joystick is unplugged, pick safe-state commands and raise a fault
            self.velWinchCmdUp = 0.0
            self.velWinchCmdDown = 0.0
            self.velXCmd = 0.0
            self.velYCmd = 0.0
            self.velTCmd = 0.0
            self.gyroResetCmd = False
            self.connectedFault.setFaulted()

            self.connectedfault.setFaulted()

        log("DI FwdRev Cmd", self.vXCmd, "mps")
        log("DI Strafe Cmd", self.vYCmd, "mps")
        log("DI Rot Cmd", self.vRotCmd, "radps")
        log("DI connective fault", self.ctrl.isConnected(), "bool")
        log("DI gyroResetCmd", self.gyroResetCmd,"bool")
    
    def getVxCmd(self):
        return self.vXCmd

    def getVyCmd(self):
        return self.vYCmd

    def getVrotCmd(self):
        return self.vRotCmd
    
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