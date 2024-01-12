import os
import wpilib
from jormungandr import choreo
from AutoSequencerV2.command import Command
from drivetrain.drivetrainControl import DrivetrainControl


class DrivePathCommand(Command):
    def __init__(self, pathFile):
        self.name = pathFile

        # Get the internal path file
        absPath = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "deploy",
                "choreo",
                pathFile + ".traj",
            )
        )

        self.path = choreo.fromFile(absPath)
        self.done = False
        self.startTime = (
            -1
        )  # we'll populate these for real later, just declare they'll exist
        self.duration = self.path.getTotalTime()
        self.drivetrain = DrivetrainControl()
        self.poseTelem = DrivetrainControl().poseEst.telemetry

    def initialize(self):
        self.startTime = wpilib.Timer.getFPGATimestamp()
        self.poseTelem.setTrajectory(self.path)

    def execute(self):
        curTime = wpilib.Timer.getFPGATimestamp() - self.startTime
        curState = self.path.sample(curTime)

        self.drivetrain.setCmdTrajectory(curState)

        self.done = curTime >= (self.duration)

        if self.done:
            self.drivetrain.setCmdRobotRelative(0, 0, 0)
            self.poseTelem.setTrajectory(None)

    def isDone(self):
        return self.done

    def getName(self):
        return f"Drive Trajectory {self.name}"
