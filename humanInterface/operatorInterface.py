#imports
from typing import Any
from wpilib import XboxController
from wpimath import applyDeadband
from utils.faults import Fault
from wpimath.filter import SlewRateLimiter

from utils.units import in2m

class operatorInterface:
    def __init__(self):
        #initialize xbox controller, important values
        #is the position commands going to be a enum later? I think they should be. 
        #But I also think that right now, they're booleans anyways. You don't change them to an enum until later? 
        #At least we didn't with shooter positions last year

        ctrlIdx = 1
        self.ctrl = XboxController(ctrlIdx)

        self.connectedFault = Fault(f"Operator XBox Controller ({ctrlIdx}) Unplugged")

        #Shooter commands
        self.shooterIntake = False
        self.shooterShoot = False
        """Idea: shouldn't shooterHold be something that happens when there is a gamepiece detected by the
        time of flight sensor? Maybe add that logic between time of flight class and the shooter wheels, 
        not operator"""
        self.shooterEject = False

        #element of the elevator. Goes up, down, and rotates into position
        self.carriageIntakePos = False
        self.carriageAmpPos = False
        self.carriageTrapPos = False
        self.carriagePodiumPos = False
        self.carriageSpeakerSubwooferPos = False

        #if the operator wants the auto align desired
        self.AutoAlignDesired = False

        #singer manual controls
        self.manualSingerUpDown = False
        self.manualSingerRot = False

        #I don't know what the max on the slew rate limiter should be. It should be a constant
        #I just made up a number... it happened to be last year's number. I just picked something
        MAX_MAN_VEL_MPS = in2m(12.0)
        self.manualSingerUpDownSlewRateLimiter = SlewRateLimiter(MAX_MAN_VEL_MPS)
        self.manualSingerRotSlewRateLimiter = SlewRateLimiter(MAX_MAN_VEL_MPS)




    def update(self):
        #update the values from the xbox controller. Updates every 20(?)ms
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
            self.AutoAlignDesired = self.ctrl.getXButton()

            #manual singer controls
            self.manualSingerUpDown = applyDeadband(self.ctrl.getLeftY(),.15)
            self.manualSingerUpDown = self.manualSingerUpDownSlewRateLimiter.calculate(self.manualSingerUpDown)
            self.manualSingerRot = applyDeadband(self.ctrl.getRightX(),.15)
            self.manualSingerRot = self.manualSingerRotSlewRateLimiter.calculate(self.manualSingerRot)

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
            self.AutoAlignDesired = False

            #manual commands
            self.manualSingerUpDown = 0
            self.manualSingerRot = 0


 #and now a bunch of functions to call 
    def getAutoAlignCmd(self):
        #returns whether auto align is desired or not
        return self.AutoAlignDesired
    
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
        #returns whether the singer is being commanded go to the position it will need to shoot from the subwoofer of the speaker
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