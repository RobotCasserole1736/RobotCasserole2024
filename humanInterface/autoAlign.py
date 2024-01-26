import math
from drivetrain.poseEstimation.drivetrainPoseEstimator import DrivetrainPoseEstimator
from drivetrain.drivetrainControl import DrivetrainControl
class AutoAlign():

    def speakerAlign(self):
        
        self.AARobotInstance = DrivetrainControl()

        self.AARobotPoseEst = self.AARobotInstance.poseEst.getCurEstPose()

        #For now I am assuming that you are on the blue alliance
        
        #if self.AARobotPoseEst.rotation().radians() <0:

        
        #returnVal = (3.1415/2) - self.AARobotPoseEst.rotation().radians()# + math.atan(self.AARobotPoseEst.Y()/self.AARobotPoseEst.X() ) #

        returnVal =math.atan(self.AARobotPoseEst.Y()/self.AARobotPoseEst.X()) - self.AARobotPoseEst.rotation().radians()# self.AARobotPoseEst.rotation().radians() - math.atan(  self.AARobotPoseEst.Y()/self.AARobotPoseEst.X()) + (3.1415/2)

        if returnVal > 0:
            returnVal = 1
        elif returnVal < 0:
            returnVal = -1


        print(f"X:{self.AARobotPoseEst.X()} Y: {self.AARobotPoseEst.Y()} rotation: {self.AARobotPoseEst.rotation().radians()}")
        print(returnVal)
        
        return returnVal 
    

        
        


        
        