from wpilib import XboxController
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from drivetrain.drivetrainPhysical import MAX_FWD_REV_SPEED_MPS
from drivetrain.drivetrainPhysical import MAX_STRAFE_SPEED_MPS
from drivetrain.drivetrainPhysical import MAX_ROTATE_SPEED_RAD_PER_SEC
from utils.faults import Fault
from utils.signalLogging import log

class DriverInterface:
    """Class to gather input from the driver of the robot"""

    def __init__(self):
        # contoller 
        ctrlIdx = 0
        self.ctrl = XboxController(ctrlIdx)
        self.vXCmd = 0
        self.vYCmd = 0
        self.vRotCmd = 0
        self.gyroResetCmd = False
        
        #Slew rate limiter
        self.vXSlewRateLimiter = SlewRateLimiter(2)
        self.vYSlewRateLimiter = SlewRateLimiter(2)
        self.vRotSlewRateLimiter = SlewRateLimiter(8)
        
        self.connectedfault = Fault(f"Driver XBox Controller ({ctrlIdx})unplugged")

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

            # Slew rate limiter
            self.vXCmd = self.vXSlewRateLimiter.calculate(velCmdXRaw)
            self.vYCmd = self.vYSlewRateLimiter.calculate(velCmdYRaw)
            self.vRotCmd = self.vRotSlewRateLimiter.calculate(velCmdRotRaw)
        

            self.gyroResetCmd = self.ctrl.getAButtonPressed()

            self.connectedfault.setNoFault()


        else:
            self.vXCmd = 0
            self.vYCmd = 0
            self.vRotCmd = 0

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