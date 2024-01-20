#imports
from typing import Any
from wpilib import XboxController
from utils.faults import Fault

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
        self.carriageSpeakerPos = False
        self.carriageTrapPos = False

        #if the operator wants the auto align desired
        self.AutoAlignDesired = False



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
            self.carriageSpeakerPos = self.ctrl.getXButton()
            self.carriageTrapPos = self.ctrl.getYButton()

            #if the operator wants the auto align desired
            self.AutoAlignDesired = self.ctrl.getXButton()

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
            self.carriageSpeakerPos = False
            self.carriageTrapPos = False

            #if the operator wants the auto align desired
            self.AutoAlignDesired = False


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
    
    def getCarriageSpeakerPosCmd(self):
        #returns whether the singer is being commanded go to the position it will need to shoot? But from where?
        return self.carriageSpeakerPos
    
    def getCarriageTrapPosCmd(self):
        #returns whether the singer is being commanded go to the position it will need for trap
        return self.carriageTrapPos
    
    #when you're using this logic, make sure there is an "else" if none of these commands are activated. 
    #In the else:, nothing should happen

    """We will use these getters with other motor-related setters, once those have been created"""