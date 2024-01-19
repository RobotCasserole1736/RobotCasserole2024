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
        self.gryoResetCmd = False
        
        #Slew rate limiter
        self.VX_SRL = SlewRateLimiter(2)
        self.VY_SRL = SlewRateLimiter(2)
        self.VRot_SRL = SlewRateLimiter(8)
        
    def update(self):
        # value of contoller buttons

        if self.ctrl.isConnected:
            VXJoyRaw = self.ctrl.getLeftX()
            VYJoyRaw = self.ctrl.getLeftY()
            VRotJoyRaw = self.ctrl.getRightX()
   
            #deadband
            VXJoy = applyDeadband(VXJoyRaw,0.15)
            VYJoy = applyDeadband(VYJoyRaw,0.15)
            VRotJoy = applyDeadband(VRotJoyRaw,0.15)
            #velocity cmd
            self.vel_CmdX = VXJoy
            self.vel_CmdY = VYJoy
            self.vel_CmdRot = VRotJoy

            
            # Slew rate limiter
            self.vel_CmdX = self.VX_SRL.calculate(VXJoyRaw)
            self.vel_CmdY = self.VY_SRL.calculate(VYJoyRaw)
            self.vel_CmdRot = self.VRot_SRL.calculate(VRotJoyRaw)
        
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

    def getGyroResetCmd(self):
        return self.gryoResetCmd