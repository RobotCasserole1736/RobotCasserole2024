import wpilib
from wpimath.geometry import Pose2d, Rotation2d, Transform2d, Translation2d
from jormungandr.choreoTrajectory import ChoreoTrajectoryState
from utils.constants import FIELD_LENGTH_FT
from utils.units import ft2m
from typing import overload

"""
 Utilities to help transform from blue alliance to red if needed
 We chose a coordinate system where the origin is always in the 
 bottom left on the blue alliance
"""


# Simple utility to check if we're on the red alliance (and therefor doing transformation is needed)
def onRed():
    return (
        wpilib.DriverStation.getAlliance() == wpilib._wpilib.DriverStation.Alliance.kRed
    )


# Base transform for X axis to flip to the other side of the field.
def transformX(in_):
    if onRed():
        return ft2m(FIELD_LENGTH_FT) - in_
    else:
        return in_


# Note that Y axis does not need any flipping

# Other types are flipped in the transform function


# The following typehints remove vscode errors by telling the linter
# exactly how the transform() function handles different types
@overload
def transform(in_: Rotation2d) -> Rotation2d:
    pass


@overload
def transform(in_: Translation2d) -> Translation2d:
    pass


@overload
def transform(in_: Pose2d) -> Pose2d:
    pass


@overload
def transform(in_: ChoreoTrajectoryState) -> ChoreoTrajectoryState:
    pass


# Actual implementation of the trasnform function
def transform(in_):
    if isinstance(in_, Rotation2d):
        if onRed():
            return Rotation2d.fromDegrees(180) - in_
        else:
            return in_

    elif isinstance(in_, Translation2d):
        if onRed():
            return Translation2d(transformX(in_.X()), in_.Y())
        else:
            return in_

    elif isinstance(in_, Transform2d):
        if onRed():
            trans = transform(in_.translation())
            rot = transform(in_.rotation())
            return Transform2d(trans, rot)
        else:
            return in_

    elif isinstance(in_, Pose2d):
        if onRed():
            trans = transform(in_.translation())
            rot = transform(in_.rotation())
            return Pose2d(trans, rot)
        else:
            return in_

    elif isinstance(in_, ChoreoTrajectoryState):
        if onRed():
            return in_.flipped()
        else:
            return in_

    else:
        raise TypeError("transform function received unknown type")
