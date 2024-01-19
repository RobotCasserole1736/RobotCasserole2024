from wpimath.kinematics import ChassisSpeeds
from wpimath.geometry import Pose2d, Rotation2d
from utils.singleton import Singleton
from utils.allianceTransformUtils import onRed

from drivetrain.poseEstimation.drivetrainPoseEstimator import DrivetrainPoseEstimator
from drivetrain.swerveModuleControl import SwerveModuleControl
from drivetrain.swerveModuleGainSet import SwerveModuleGainSet
from drivetrain.drivetrainTrajectoryControl import DrivetrainTrajectoryControl
from drivetrain.drivetrainPhysical import (
    FL_ENCODER_MOUNT_OFFSET_RAD,
    MAX_FWD_REV_SPEED_MPS,
)
from drivetrain.drivetrainPhysical import FR_ENCODER_MOUNT_OFFSET_RAD
from drivetrain.drivetrainPhysical import BL_ENCODER_MOUNT_OFFSET_RAD
from drivetrain.drivetrainPhysical import BR_ENCODER_MOUNT_OFFSET_RAD
from drivetrain.drivetrainPhysical import kinematics


class DrivetrainControl(metaclass=Singleton):
    """
    Top-level control class for controlling a swerve drivetrain
    """

    def __init__(self):
        self.modules = []
        self.modules.append(
            SwerveModuleControl("FL", 2, 3, 0, FL_ENCODER_MOUNT_OFFSET_RAD, False)
        )
        self.modules.append(
            SwerveModuleControl("FR", 4, 5, 1, FR_ENCODER_MOUNT_OFFSET_RAD, True)
        )
        self.modules.append(
            SwerveModuleControl("BL", 6, 7, 2, BL_ENCODER_MOUNT_OFFSET_RAD, False)
        )
        self.modules.append(
            SwerveModuleControl("BR", 8, 9, 3, BR_ENCODER_MOUNT_OFFSET_RAD, True)
        )

        self.desChSpd = ChassisSpeeds()
        self.curDesPose = Pose2d()

        self.gains = SwerveModuleGainSet()

        self.poseEst = DrivetrainPoseEstimator(self.getModulePositions())

        self.trajCtrl = DrivetrainTrajectoryControl()

        self._updateAllCals()

    def setCmdFieldRelative(self, velX, velY, velT):
        """Send commands to the robot for motion relative to the field

        Args:
            velX (float): Desired speed in the field's X direction, in meters per second
            velY (float): Desired speed in the field's Y axis, in th meters per second
            velT (float): Desired rotational speed in the field's reference frame, in radians per second
        """
        tmp = ChassisSpeeds.fromFieldRelativeSpeeds(
            velX, velY, velT, self.poseEst.getCurEstPose().rotation()
        )
        self.desChSpd = _discretizeChSpd(tmp)
        self.poseEst.telemetry.setDesiredPose(self.poseEst.getCurEstPose())

    def setCmdRobotRelative(self, velX, velY, velT):
        """Send commands to the robot for motion relative to its own reference frame

        Args:
            velX (float): Desired speed in the robot's X direction, in meters per second
            velY (float): Desired speed in the robot's Y axis, in th meters per second
            velT (float): Desired rotational speed in the robot's reference frame, in radians per second
        """
        self.desChSpd = _discretizeChSpd(ChassisSpeeds(velX, velY, velT))
        self.poseEst.telemetry.setDesiredPose(self.poseEst.getCurEstPose())

    def setCmdTrajectory(self, cmd):
        """Send commands to the robot for motion as a part of following a trajectory

        Args:
            cmd (PathPlannerState): PathPlanner trajectory sample for the current time
        """
        tmp = self.trajCtrl.update(cmd, self.poseEst.getCurEstPose())
        self.desChSpd = _discretizeChSpd(tmp)
        self.poseEst.telemetry.setDesiredPose(cmd.getPose())

    def update(self):
        """
        Main periodic update, should be called every 20ms
        """

        # Given the current desired chassis speeds, convert to module states
        desModStates = kinematics.toSwerveModuleStates(self.desChSpd)

        # Scale back commands if one corner of the robot is going too fast
        kinematics.desaturateWheelSpeeds(desModStates, MAX_FWD_REV_SPEED_MPS)

        # Send commands to modules and update
        for idx, module in enumerate(self.modules):
            module.setDesiredState(desModStates[idx])
            module.update()

        # Update the estimate of our pose
        self.poseEst.update(self.getModulePositions(), self.getModuleSpeeds())

        # Update calibration values if they've changed
        if self.gains.hasChanged():
            self._updateAllCals()

    def _updateAllCals(self):
        # Helper function - updates all calibration on request
        for module in self.modules:
            module.setClosedLoopGains(self.gains)

    def getModulePositions(self):
        """
        Returns:
            Tuple of the actual module positions (as read from sensors)
        """
        return tuple(mod.getActualPosition() for mod in self.modules)

    def getModuleSpeeds(self):
        """
        Returns:
            Tuple of the actual module speeds (as read from sensors)
        """
        return tuple(mod.getActualState() for mod in self.modules)

    def resetGyro(self):
        # Update pose estimator to think we're at the same translation,
        # but aligned facing downfield
        curTranslation = self.poseEst.getCurEstPose().translation()
        newGyroRotation = Rotation2d(0.0) if(onRed()) else Rotation2d(180.0)
        newPose = Pose2d(curTranslation, newGyroRotation)
        self.poseEst.setKnownPose(newPose)


def _discretizeChSpd(chSpd):
    """See https://www.chiefdelphi.com/t/whitepaper-swerve-drive-skew-and-second-order-kinematics/416964/30
        Corrects for 2nd order kinematics
        Should be included in wpilib 2024, but putting here for now

    Args:
        chSpd (ChassisSpeeds): ChassisSpeeds input

    Returns:
        ChassisSpeeds: Adjusted ch speed
    """
    dt = 0.02
    poseVel = Pose2d(chSpd.vx * dt, chSpd.vy * dt, Rotation2d(chSpd.omega * dt))
    twistVel = Pose2d().log(poseVel)
    return ChassisSpeeds(twistVel.dx / dt, twistVel.dy / dt, twistVel.dtheta / dt)
