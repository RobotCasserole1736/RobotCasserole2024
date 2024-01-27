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

        #returnVal = ( 2*math.pi +math.atan(self.AARobotPoseEst.Y()/self.AARobotPoseEst.X()) - 3.1415 ) - (self.AARobotPoseEst.rotation().radians() )# self.AARobotPoseEst.rotation().radians() - math.atan(  self.AARobotPoseEst.Y()/self.AARobotPoseEst.X()) + (3.1415/2)
        returnVal = ( math.atan((self.AARobotPoseEst.Y() - 2)/(self.AARobotPoseEst.X() - 2)) - 3.1415 ) % (2*math.pi) - (self.AARobotPoseEst.rotation().radians() )
        if abs(returnVal) > math.pi:
            returnVal = ((2* math.pi) - returnVal) * -1
        
        #We need to detect if we are on the left of the point and if we are dont subtract by pi. look at the board for how to change the point that the robot is pointing at
        #currently pointing at a position 2 units above and 2 units to the right of (0,0)

        if returnVal > 0:
            returnVal = 1
        elif returnVal < 0:
            returnVal = -1

        print(f"current:{math.degrees(self.AARobotPoseEst.rotation().radians())} wanted: {math.degrees(2*math.pi + math.atan(self.AARobotPoseEst.Y()/self.AARobotPoseEst.X()) - 3.1415)}")
        

        #print(f"X:{self.AARobotPoseEst.X()} Y: {self.AARobotPoseEst.Y()} rotation: {self.AARobotPoseEst.rotation().radians()}")
        #print(returnVal)
        
        return returnVal 
    

        
        


        
        