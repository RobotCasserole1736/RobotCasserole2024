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
    def transformX(in):
        if DriverStation.getAlliance() == AllianceStationID.Red:
            return Constants.FIELD_LENGTH_M - in
        else:
            return in
    
    def transformY(in):
        return in

