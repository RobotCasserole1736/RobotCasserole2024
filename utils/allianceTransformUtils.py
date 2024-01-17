import wpilib
from wpimath.geometry import Pose2d, Rotation2d, Transform2d, Translation2d
from jormungandr.choreoTrajectory import ChoreoTrajectoryState
from utils.constants import FIELD_LENGTH_FT
from utils.units import ft2m

"""
 Utilities to help transform from blue alliance to red if needed
 We went rogue and chose a coordinate system where the origin is always in the 
 bottom left on the blue alliance
"""
class AllianceTransformUtils:
    #We think the code makes sense. We just don't have the actual values and don't know where they are.
    @staticmethod
    def transformX(in_):
        if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
            return (ft2m(FIELD_LENGTH_FT) - in_)
        else:
            return in_

    def transformY(self,in_):
        return in_

    def transform(self,in_):
        if isinstance(in_,Rotation2d):
            if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
                return (Rotation2d.fromDegrees(180) - in_)
            else: 
                return in_

        elif isinstance(in_,Translation2d):
            if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
                return Translation2d(self.transformX(in_.X()), in_.Y())
            else:
                return in_
        
        elif isinstance(in_,Transform2d):
            if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
                translation = self.transform(in_.translation())
                rotation = self.transform(in_.rotation())
                return Transform2d(translation, rotation)
            else:
                return in_
        
        elif isinstance(in_,Pose2d):
            if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
                trans = self.transform(in_.translation())
                rot = self.transform(in_.rotation())
                return Pose2d(trans, rot)
            else:
                return in_

    def transformChoreoTrajectoryState(self,input):
        if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
            return input.flipped()
        else:
            return input