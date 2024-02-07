#imports
from wpilib import XboxController
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from singerMovement.singerConstants import MAX_MAN_VEL_MPS, MAX_MANUAL_DEG_PER_SEC, MAX_MANUAL_ROT_ACCEL_DEGPS2, MAX_MAN_ACCEL_MPS2
from utils.faults import Fault
from utils.signalLogging import log
from utils.units import in2m
from drivetrain.controlStrategies.autoDrive import AutoDrive
from singerMovement.carriageControl import CarriageControl

class OperatorInterface:
    def __init__(self):
        #initialize xbox controller, important values

        ctrlIdx = 1
        self.ctrl = XboxController(ctrlIdx)

        self.connectedFault = Fault(f"Operator XBox Controller ({ctrlIdx}) Unplugged")
        self.AutoDrive = AutoDrive()
        #Shooter commands
        self.singerIntake = False
        self.singerShoot = False
        self.singerEject = False

        #element of the elevator. Goes up, down, and rotates into position
        self.carriageIntakePos = False
        self.carriageAmpPos = False
        self.carriageTrapPos = False
        self.carriagePodiumPos = False
        self.carriageSpeakerSubwooferPos = False

        #if the operator wants the auto align desired
        self.AutoDrive = False

        #singer manual controls
        self.manualSingerUpDown = 0
        self.manualSingerRot = 0

        #I don't know what the max on the slew rate limiter should be. It should be a constant
        self.manualSingerUpDownSlewRateLimiter = SlewRateLimiter(MAX_MAN_ACCEL_MPS2)
        self.manualSingerRotSlewRateLimiter = SlewRateLimiter(MAX_MANUAL_ROT_ACCEL_DEGPS2)
        
        self.motorRotations = 0
        self.LinearDisp = 0




    def update(self):
        #update the values from the xbox controller. Updates every 20ms
        #Make sure there's logic for if a controller is connected and nothing happens if it doesn't

        if self.ctrl.isConnected():

            #Singer commands
            self.singerIntake = self.ctrl.getRightBumper()
            self.singerShoot = self.ctrl.getRightTriggerAxis() > .5
            self.singerEject = self.ctrl.getLeftBumper()

            #element of the elevator. Goes up, down, and rotates into position
            self.carriageIntakePos = self.ctrl.getAButton()
            self.carriageAmpPos = self.ctrl.getBButton()
            self.carriageTrapPos = self.ctrl.getYButton()
            self.carriageSpeakerSubwooferPos = 225 < self.ctrl.getPOV() < 315
            #Above is basically the left side of the D pad
            self.carriagePodiumPos = 45 < self.ctrl.getPOV() < 135
            #Above is basically the right side of the D pad

            #if the operator wants the auto align desired
            if self.ctrl.getXButton() == True:
                AutoDrive().setCmd(True)
                self.autoAlignDesired = True
            else:
                AutoDrive().setCmd(False)
                self.autoAlignDesired = False
            #manual singer controls

            self.singerUpDownJoy = applyDeadband(self.ctrl.getLeftY(),.15)
            self.manualSingerUpDownRaw = self.singerUpDownJoy * MAX_MAN_VEL_MPS
            self.manualSingerUpDown = self.manualSingerUpDownSlewRateLimiter.calculate(self.manualSingerUpDownRaw)

            self.singerRotJoy = applyDeadband(self.ctrl.getRightY(),.15)
            self.manualSingerRotRaw = self.singerRotJoy * MAX_MANUAL_DEG_PER_SEC
            self.manualSingerRot = self.manualSingerRotSlewRateLimiter.calculate(self.manualSingerRotRaw)

            self.connectedFault.setNoFault()

        else:
            self.connectedFault.setFaulted()

            #Singer commands
            self.singerIntake = False
            self.singerShoot = False
            self.singerEject = False

            #element of the elevator. Goes up, down, and rotates into position
            self.carriageIntakePos = False
            self.carriageAmpPos = False
            self.carriageTrapPos = False
            self.carriageSpeakerSubwooferPos = False
            self.carriagePodiumPos = False

            #if the operator wants the auto align desired
            self.autoAlignDesired = False

            #manual commands
            self.manualSingerUpDown = 0
            self.manualSingerRot = 0

        #log("OI AutoAlign Cmd", self.autoAlignDesired, "bool")
        log("OI Singer Intake Cmd", self.singerIntake, "bool")
        log("OI Singer Shoot Cmd", self.singerShoot, "bool")
        log("OI Singer Eject Cmd", self.singerEject, "bool")
        log("OI Carriage Intake Pos Cmd", self.carriageIntakePos, "bool")
        log("OI Carriage Amp Pos Cmd", self.carriageAmpPos, "bool")
        log("OI Carriage Trap Pos Cmd", self.carriageTrapPos, "bool")
        log("OI Carriage Speaker/Subwoofer Pos Cmd", self.carriageSpeakerSubwooferPos, "bool")
        log("OI Carriage Podium Pos Cmd", self.carriagePodiumPos, "bool")
        log("OI Manual Singer Up/Down Cmd", self.manualSingerUpDown, "mps")
        log("OI Manual Singer Rot Cmd", self.manualSingerRot, "deg/s")


 #and now a bunch of functions to call 
    def getAutoAlignCmd(self):
        #returns whether auto align is desired or not
        return self.autoAlignDesired
    
    def singerIsCmdd(self):
        return self.singerIntake or self.singerShoot or self.singerEject
    
    def getSingerIntakeCmd(self):
        #returns whether the singer is being commanded to intake
        return self.singerIntake
    
    def getSingerShootCmd(self):
        #returns whether the singer is being commanded to shoot
        return self.singerShoot
    
    def getSingerEjectCmd(self):
        #returns whether the singer is being commanded to eject
        return self.singerEject

    """Robot.py logic? What about shooter in the speaker vs the amp, 
    and do we need different amounts of shooter wheel power depending on where the robot is 
    Also, what happens when multiple of these things are being commanded. Need logic for that too
        If singerIsCmdd:
            if getsingerIntakeCmd:
                send something to the class that controls the actual rollers.
            if getSingerShootCmd:
                send something to the class that controls the rollers
            if getSingerEjectCmd:
                again, send something to the rollers
        else:
            just don't do anything (pass?)
            """
     
    def getCarriageIntakePosCmd(self):
        #returns whether the singer is being commanded go to intake position
        return self.carriageIntakePos
    
    def getCarriageAmpPosCmd(self):
        #returns whether the singer is being commanded go to amp position
        return self.carriageAmpPos
    
    def getCarriageTrapPosCmd(self):
        #returns whether the singer is being commanded go to the position it will need for trap
        return self.carriageTrapPos
    
    def getCarriageSpeakerSubwooferPosCmd(self):
        #returns whether the singer is being commanded go to the position it will need to shoot 
        #from the subwoofer of the speaker
        return self.carriageSpeakerSubwooferPos
    
    def getCarriagePodiumPosCmd(self):
        #returns whether the singer is being commanded go to the position it will need to shoot from the podium
        return self.carriagePodiumPos
    
    #when you're using this logic, make sure there is an "else" if none of these commands are activated. 
    #In the else:, nothing should happen

    """We will use these getters with other motor-related setters, once those have been created"""

    #if the manual commands to control the singer are active, we will have to know that and get them later
    def manCmdActive(self):
        return  self.manualSingerUpDown != 0 or self.manualSingerRot != 0

    #this will be joystick command for degrees
    def manSingerRotCmd(self):
        return self.manualSingerRot

    #this will be joystick command for going up/down
    def manSingerUpDown(self):
        return self.manSingerUpDown