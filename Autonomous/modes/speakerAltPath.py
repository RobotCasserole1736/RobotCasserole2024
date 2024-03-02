from AutoSequencerV2.mode import Mode
from Autonomous.commands.drivePathCommand import DrivePathCommand
from Autonomous.commands.speakerShootCommand import SpeakerShootCommand
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup

class speakerAltPath(Mode):
    def __init__(self):
        Mode.__init__(self, f"speaker alt path")
        self.SequentialCommandGroup = SequentialCommandGroup()
        self.pathCmd = DrivePathCommand("Speaker_alternate_path")
        #self.shoot = SpeakerShootCommand()
        self.commandList = [self.pathCmd]
    
    def getCmdGroup(self):
        # Return shoot, then path command
        return SequentialCommandGroup(self.commandList)

    def getInitialDrivetrainPose(self):
        # Use the path command to specify the starting pose
        return self.pathCmd.path.getInitialPose()
