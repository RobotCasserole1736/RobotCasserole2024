import wpilib
from wpilib import DriverStation
from hal import AllianceStationID

from wpimath.geometry import Pose2d, Rotation2d, Transform2d, Translation2d

from utils.constants import FIELD_LENGTH_FT

from utils.units import m2ft

"""
 Utilities to help transform from blue alliance to red if needed
 We went rogue and chose a coordinate system where the origin is always in the 
 bottom left on the blue alliance
"""
class AllianceTransformUtils:


    @staticmethod
    def transformX(input):
        if DriverStation.getAlliance() == AllianceStationID.Red: # type: ignore
            return m2ft(FIELD_LENGTH_FT) - input
        else:
            return input
    
    def transformY(input):
        return input

