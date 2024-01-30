import math
from drivetrain.poseEstimation.drivetrainPoseEstimator import DrivetrainPoseEstimator
from drivetrain.drivetrainControl import DrivetrainControl

class AutoAlign():

    def speakerAlign(self,targetX,targetY):
        
        self.AARobotInstance = DrivetrainControl()

        self.AARobotPoseEst = self.AARobotInstance.poseEst.getCurEstPose()

        #For now I am assuming that you are on the blue alliance
        
        self.targetX = targetX
        self.targetY = targetY
        #I am currently declairing these as test variables. They store the target X and Y.
        

        if self.AARobotPoseEst.X() - self.targetX > 0: # test to see if we are to the right of the robot
            #If we are, we have to correct the angle by 1 pi
            returnVal = ( math.atan((self.AARobotPoseEst.Y() - targetY)/(self.AARobotPoseEst.X() - self.targetX)) - math.pi ) % (2*math.pi) - (self.AARobotPoseEst.rotation().radians() )
        else:
            #If we aren't, we don't need to.
            returnVal = ( math.atan((self.AARobotPoseEst.Y() - targetY)/(self.AARobotPoseEst.X() - self.targetX)) ) % (2*math.pi) - (self.AARobotPoseEst.rotation().radians() )
        
        #Test if the angle we calculated will be greater than 180 degrees. If it is, reverse it.
        if abs(returnVal) > math.pi:
            returnVal = ((2* math.pi) - returnVal) * -1
        
        #We need to detect if we are on the left of the point and if we are dont subtract by pi. look at the board for how to change the point that the robot is pointing at
        #currently pointing at a position 2 units above and 2 units to the right of (0,0)


        #We will need to update this to make it faster. It moves according to if the angle difference is positive or negative.
            '''
        if returnVal > 0:
            returnVal = 2
        elif returnVal < 0:
            returnVal = -2
        '''
            
        self.XVelAvg = (self.AARobotInstance.getModuleSpeeds()[0])# + self.AARobotInstance.getModuleSpeeds()[1].X() + self.AARobotInstance.getModuleSpeeds()[2].X() + self.AARobotInstance.getModuleSpeeds()[3].X())/3
        self.YVelAvg = (self.AARobotInstance.getModuleSpeeds()[0])# + self.AARobotInstance.getModuleSpeeds()[1].Y() + self.AARobotInstance.getModuleSpeeds()[2].Y() + self.AARobotInstance.getModuleSpeeds()[3].Y())/3

        self.AARobotInstance.setCmdFieldRelative(self.XVelAvg, self.YVelAvg, returnVal)
        #Emergency debuging print, delete hash in case of bug related emergency:
        #print(f"current:{math.degrees(self.AARobotPoseEst.rotation().radians())} wanted: {math.degrees(2*math.pi + math.atan(self.AARobotPoseEst.Y()/self.AARobotPoseEst.X()) - 3.1415)}")
        

        
        
        return 0
    

        
        


        
        