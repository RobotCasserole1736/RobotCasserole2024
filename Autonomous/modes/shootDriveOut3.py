from AutoSequencerV2.mode import Mode
from Autonomous.commands.drivePathCommand import DrivePathCommand
from Autonomous.commands.speakerShootCommand import SpeakerShootCommand
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup

class ShootDriveOut3(Mode):
    def __init__(self):
        Mode.__init__(self, f"Shoot Drive Out 3")
        self.SequentialCommandGroup = SequentialCommandGroup()
        self.pathCmd = DrivePathCommand("DriveOut3")
        self.shoot = SpeakerShootCommand()
        self.commandList = [self.shoot, self.pathCmd]
    
    def getCmdGroup(self):
        # Return shoot, then path command
        return SequentialCommandGroup(self.commandList)

    def getInitialDrivetrainPose(self):
        # Use the path command to specify the starting pose
        return self.pathCmd.path.getInitialPose()
