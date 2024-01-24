import math
from drivetrain.poseEstimation.drivetrainPoseEstimator import DrivetrainPoseEstimator
from drivetrain.drivetrainControl import DrivetrainControl
class AutoAlign():

    def speakerAlign(self):
        
        self.AARobotInstance = DrivetrainControl()

        self.AARobotPoseEst = self.AARobotInstance.poseEst.getCurEstPose()

        #For now I am assuming that you are on the blue alliance
        
        
        returnVal = self.AARobotPoseEst.rotation().radians() - math.atan(5.547868 - self.AARobotPoseEst.Y()/self.AARobotPoseEst.X() )
        print(returnVal)
        if returnVal >= 0 :
            return returnVal * -1
        else:
            return returnVal 
        


        
        