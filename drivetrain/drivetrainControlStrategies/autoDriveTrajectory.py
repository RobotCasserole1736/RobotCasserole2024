


from drivetrain.drivetrainControl import DrivetrainControl
from drivetrain.drivetrainCommand import DrivetrainCommand
from drivetrain.controlStrategies.holonomicDriveController import HolonomicDriveController
from jormungandr.choreo import ChoreoTrajectoryState
from utils.singleton import Singleton

class AutoDriveTrajectory(metaclass=Singleton):

    def __init__(self):
        self.trajCtrl = HolonomicDriveController()
        self.curTrajCmd = None
        self.dt = DrivetrainControl()



    def setCmdTrajectory(self, cmd:ChoreoTrajectoryState):
        """Send commands to the robot for motion as a part of following a trajectory

        Args:
            cmd (PathPlannerState): PathPlanner trajectory sample for the current time, or None for inactive.
        """
        self.curTrajCmd = cmd



    def update(self, cmd_in:DrivetrainCommand) -> DrivetrainCommand:

        if(self.curTrajCmd is not None):
            return self.trajCtrl.update(self.curTrajCmd, self.dt.getCurEstPose())
        else:
            return cmd_in

