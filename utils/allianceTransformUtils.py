import wpilib
from wpilib import DriverStation
from hal import AllianceStationID

from wpimath.geometry import Pose2d, Rotation2d, Transform2d, Translation2d
from wpimath.geometry import Pose2d, Rotation2d, Transform2d, Translation2d
from wpimath.geometry import Pose2d, Rotation2d, Transform2d, Translation2d
from wpimath.geometry import Pose2d, Rotation2d, Transform2d, Translation2d
from wpimath.geometry import Pose2d, Rotation2d, Transform2d, Translation2d

"""
 Utilities to help transform from blue alliance to red if needed
 We went rogue and chose a coordinate system where the origin is always in the 
 bottom left on the blue alliance
"""
class AllianceTransformUtils:
    @staticmethod
    def transformX( self, input):
        
        if wpilib._wpilib.DriverStation.Alliance == Alliance.kRed:
            return 16.4592 - input
        else:
            return input
    
    def transformY(self,input):
        return input
    
    def Rotation2d(self,input):
        if wpilib._wpilib.DriverStation.Alliance == Alliance.kRed:
            return Rotation2d.fromDegrees(180).minus(input)
        else: 
            return input 

    def Translation2d(self,input):
        if wpilib._wpilib.DriverStation.Alliance == Alliance.kRed:
            return Translation2d(AllianceTransformUtils.transformX(input.getX()), input.getY())
        else:
            return input
    
    def Transform2d(self,input):
        if wpilib._wpilib.DriverStation.Alliance == Alliance.kRed:
            trans = AllianceTransformUtils.transform(input.getTranslation())
            rot = AllianceTransformUtils.transform(input.getRotation())
            return Transform2d(trans, rot)
        else:
            return input
        
    def Pose2d(self,input):
        if wpilib._wpilib.DriverStation.Alliance == Alliance.kRed:
            trans = AllianceTransformUtils.transform(input.getTranslation())
            rot = AllianceTransformUtils.transform(input.getRotation())
            return Pose2d(trans, rot)
        else:
            return input
    
    def transformChoreoTrajectoryState(self,input):
        if wpilib._wpilib.DriverStation.Alliance == Alliance.kRed:
            return input.flipped()
        else:
            return input
