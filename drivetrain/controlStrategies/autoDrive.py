import math
from wpimath.geometry import Pose2d
from drivetrain.drivetrainCommand import DrivetrainCommand
from utils.allianceTransformUtils import onRed
from utils.allianceTransformUtils import transform
from utils.singleton import Singleton


class AutoDrive(metaclass=Singleton):
    def __init__(self):
        self.active = False
        self.AARobotPoseEst = None

    def setCmd(self, shouldAutoAlign):
        """Automatically point the drivetrain toward the speaker

        Args:
            shouldAutoAlign (PathPlannerState): PathPlanner trajectory 
            sample for the current time, or None for inactive.
        """
        self.active = shouldAutoAlign

    def update(self, cmdIn: DrivetrainCommand, curPose: Pose2d) -> DrivetrainCommand:
        if self.active:
            
            
            return (
                self.speakerAlign(
                curPose, cmdIn
                )   
            )  
        else:
            return cmdIn

    def speakerAlign(self, curPose,cmdIn):
        self.AARobotPoseEst = curPose
        
        
        #Find out if we are on red team
        if onRed() == True:#If we are, set the target pos to the pos of the red speaker
            self.targetX = 16.54175 - 0.22987
            self.targetY = 5.4572958333417994
        else: #If we aren't, set the target pos to the pos of the blue speaker
            self.targetX = 0.22987
            self.targetY = 5.4572958333417994



        
        
        

        if self.AARobotPoseEst.X() - self.targetX > 0: # test to see if we are to the right of the robot
            #If we are, we have to correct the angle by 1 pi. This is built into the following equation
            returnVal = ( math.atan((self.AARobotPoseEst.Y() - self.targetY)/(self.AARobotPoseEst.X() - self.targetX)) - math.pi ) % (2*math.pi) - (self.AARobotPoseEst.rotation().radians() )
        else:
            #If we aren't, we don't need to. (these eqations are the same except the other one subtracts by pi and this one doesn't)
            returnVal = ( math.atan((self.AARobotPoseEst.Y() - self.targetY)/(self.AARobotPoseEst.X() - self.targetX)) ) % (2*math.pi) - (self.AARobotPoseEst.rotation().radians() )
        
        #Test if the angle we calculated will be greater than 180 degrees. If it is, reverse it.
        if abs(returnVal) > math.pi:
            returnVal = ((2* math.pi) - returnVal) * -1
        
        

        if abs(returnVal) <= 0.05: #Check to see if we are making a really small correction. if we are, don't worry about it. We only need a certain level of accuracy.
            returnVal = 0
        


        returnDriveTrainCommand = DrivetrainCommand() #We create an instance of DrivetrainCommand and configure it.
        returnDriveTrainCommand.velT = returnVal * 5 #set the rotational vel to 5 * the angle we calculated. We multiply it by 5 so its faster :o
        returnDriveTrainCommand.velX = cmdIn.velX #set the X vel to the original X vel.
        returnDriveTrainCommand.velY = cmdIn.velY #Set the Y vel to the original Y vel.
        return returnDriveTrainCommand
        
    
