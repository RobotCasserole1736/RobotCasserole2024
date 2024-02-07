import os
import wpilib
from drivetrain.controlStrategies.trajectory import Trajectory
from drivetrain.drivetrainControl import DrivetrainControl
from jormungandr import choreo
from AutoSequencerV2.command import Command
from utils.allianceTransformUtils import transform


class EjectCommand(Command):
    def __init__(self, pathFile):
        
        #self.duration = self.path.getTotalTime()

        self.done = False
        self.startTime = (
            -1
        )  # we'll populate these for real later, just declare they'll exist

    def execute(self):
        curTime = wpilib.Timer.getFPGATimestamp() - self.startTime

        #self.done = curTime >= (self.duration)

    def isDone(self):
        pass
        #return self.done