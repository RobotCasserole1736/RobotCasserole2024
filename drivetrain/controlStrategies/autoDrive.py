import math
from wpimath.geometry import Pose2d
from drivetrain.drivetrainCommand import DrivetrainCommand
from singerMovement.carriageControl import CarriageControl
from utils.allianceTransformUtils import onRed
from utils.signalLogging import log
from utils.singleton import Singleton

class AutoDrive(metaclass=Singleton):
    def __init__(self):
        self.active = False
        self.AARobotPoseEst = Pose2d()
        self.returnDriveTrainCommand = DrivetrainCommand()

    def setCmd(self, shouldAutoAlign: bool):
        self.active = shouldAutoAlign

    def update(self, cmdIn: DrivetrainCommand, curPose: Pose2d) -> DrivetrainCommand:
        if self.active:
            return self.speakerAlign(curPose, cmdIn)
        else:
            return cmdIn

    def getDesiredAngle(self, curPose):
        # Find out if we are on red team
        # If we are, set the target pos to the pos of the red speaker
        if onRed() == True:
            self.targetX = 16.54175 - 0.22987
            self.targetY = 5.4572958333417994
        # If we aren't, set the target pos to the pos of the blue speaker
        else:
            self.targetX = 0.22987
            self.targetY = 5.4572958333417994
        distX = curPose.X() - self.targetX
        distY = curPose.Y() - self.targetY
        singerHeight = 1
        targetHeight = 2.0385024 - singerHeight
        distFromTarget = math.sqrt(math.pow(distX , 2) + math.pow(distY , 2))
        noteTravelPath = math.sqrt(math.pow(targetHeight , 2) + math.pow(distFromTarget , 2))
        self.desiredAngle = math.acos(distFromTarget / noteTravelPath)

        log("Singer Allign desired angle", self.desiredAngle)
        log("Singer Allign DistX, DistY", (distX,distY))

        CarriageControl().setSignerAutoAlignAngle(self.desiredAngle)

    def speakerAlign(self, curPose,cmdIn):
        self.AARobotPoseEst = curPose
        
        # Find out if we are on red team
        # If we are, set the target pos to the pos of the red speaker
        if onRed() == True:
            self.targetX = 16.54175 - 0.22987
            self.targetY = 5.4572958333417994

        # If we aren't, set the target pos to the pos of the blue speaker
        else:
            self.targetX = 0.22987
            self.targetY = 5.4572958333417994
        # Test to see if we are to the right of the robot
        # If we are, we have to correct the angle by 1 pi
        # This is built into the following equation
        if self.AARobotPoseEst.X() - self.targetX > 0:
            returnVal = ( math.atan((self.AARobotPoseEst.Y() \
                            - self.targetY)/(self.AARobotPoseEst.X() \
                            - self.targetX)) - math.pi ) % (2*math.pi) \
                            - (self.AARobotPoseEst.rotation().radians() )
        # If we aren't, we don't need to. 
        # (these eqations are the same except the other one subtracts by pi and this one doesn't)
        else:
            returnVal = ( math.atan((self.AARobotPoseEst.Y() \
                            - self.targetY)/(self.AARobotPoseEst.X() \
                            - self.targetX)) ) % (2*math.pi) \
                            - (self.AARobotPoseEst.rotation().radians() )

        # Test if the angle we calculated will be greater than 180 degrees
        # If it is, reverse it
        if abs(returnVal) > math.pi:
            returnVal = ((2* math.pi) - returnVal) * -1

        # Check to see if we are making a really small correction
        # If we are, don't worry about it. We only need a certain level of accuracy
        if abs(returnVal) <= 0.05:
            returnVal = 0
        # Set the rotational vel to 5 * the angle we calculated
        # We multiply it by 5 so its faster :o
        self.returnDriveTrainCommand.velT = returnVal * 5
        self.returnDriveTrainCommand.velX = cmdIn.velX # Set the X vel to the original X vel
        self.returnDriveTrainCommand.velY = cmdIn.velY # Set the Y vel to the original Y vel
        return self.returnDriveTrainCommand