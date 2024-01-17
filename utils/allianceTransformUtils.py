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

    def transformRotation(self,in_):
        if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
            return (Rotation2d.fromDegrees(180) - in_)
        else: 
            return in_

    def transformTranslation(self,in_): 
        if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
            #return Translation2d(self, AllianceTransformUtils.transformX(x value), AllianceTranformUtils.transformY(y value))
            #We need to get an x to transform it, but we don't know where to get said x from. Same with y
            return in_
        else:
            return in_

    def transformTransform(self,in_):
        if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
            #translation = Transform2d((self, AllianceTransformUtils.transformX(x value), AllianceTranformUtils.transformY(y value)))
            #rotation = AllianceTransformUtils.transformRotation(rotation value)
            #return Transform2d(self, translation, rotation)
            return in_
        else:
            return in_

    def transformPose(self,in_):
        if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
            #trans = AllianceTransformUtils.transformTranlation(translation value)
            #rot = AllianceTransformUtils.transformPose(rotation)
            #return Pose2d(trans, rot)
            return in_
        else:
            return in_

    def transformChoreoTrajectoryState(self,input):
        if wpilib._wpilib.DriverStation.Alliance == wpilib._wpilib.DriverStation.Alliance.kRed:
            return input.flipped()
        else:
            return input