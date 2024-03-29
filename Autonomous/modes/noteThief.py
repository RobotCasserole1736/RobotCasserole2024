from Autonomous.commands.drivePathCommand import DrivePathCommand
from AutoSequencerV2.mode import Mode


# big ole L shape to mess up other autonomous
class NoteThief(Mode):
    def __init__(self):
        Mode.__init__(self, f"Note Thief")
        self.pathCmd = DrivePathCommand("NoteThief")

    def getCmdGroup(self):
        # Just return the path command
        return self.pathCmd

    def getInitialDrivetrainPose(self):
        # Use the path command to specify the starting pose
        return self.pathCmd.path.getInitialPose()
