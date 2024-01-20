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
        
        self.connectedfault = Fault(f"Driver XBox Controller ({CtrlIdx})unplugged")

    def update(self):
        # value of contoller buttons

        if self.ctrl.isConnected:
            VXJoyRaw = self.ctrl.getLeftY() * -1
            VYJoyRaw = self.ctrl.getLeftX() * -1
            VRotJoyRaw = self.ctrl.getRightX() * -1
   
            #deadband
            VXJoy = applyDeadband(VXJoyRaw,0.15)
            VYJoy = applyDeadband(VYJoyRaw,0.15)
            VRotJoy = applyDeadband(VRotJoyRaw,0.15)

            slowMult = .5 if (self.ctrl.getRightBumper()) else 1.0

            #velocity cmd
            vel_CmdXRaw = VXJoy * MAX_STRAFE_SPEED_MPS * slowMult
            vel_CmdYRaw = VYJoy * MAX_FWD_REV_SPEED_MPS * slowMult
            vel_CmdRotRaw = VRotJoy * MAX_ROTATE_SPEED_RAD_PER_SEC

            # Slew rate limiter
            self.vXCmd = self.VX_SRL.calculate(vel_CmdXRaw)
            self.vYCmd = self.VY_SRL.calculate(vel_CmdYRaw)
            self.vRotCmd = self.VRot_SRL.calculate(vel_CmdRotRaw)
        

            self.GyroResetCmd = self.ctrl.getAButtonPressed()

            self.connectedfault.setNoFault()


        else:
            self.vXCmd = 0
            self.vYCmd = 0
            self.vRotCmd = 0

            self.connectedfault.setFaulted()

        log("DI FwdRev Cmd", self.vXCmd, "mps")
        log("DI FwdRev Cmd", self.vYCmd, "mps")
        log("DI Rot Cmd", self.vRotCmd, "radps")
        log("DI connective fault", self.ctrl.isConnected(), "bool")
       
    
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
        return self.gryoResetCmd