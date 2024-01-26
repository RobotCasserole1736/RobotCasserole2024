
from drivetrain.drivetrainCommand import DrivetrainCommand
from utils.singleton import Singleton
from wpimath.geometry import Pose2d

class AutoDrive(metaclass=Singleton):

    def __init__(self):
        self.active = False


    def setCmd(self, shouldAutoAlign):
        """Automatically point the drivetrain toward the speaker

        Args:
            shouldAutoAlign (PathPlannerState): PathPlanner trajectory sample for the current time, or None for inactive.
        """
        self.active = shouldAutoAlign



    def update(self, cmd_in:DrivetrainCommand, curPose:Pose2d) -> DrivetrainCommand:

        if(self.active):
            # TODO - calculate a DrivetrainCommand that keeps us pointed at the speaker
            return DrivetrainCommand()
        else:
            return cmd_in

