from AutoSequencerV2.parallelCommandGroup import ParallelCommandGroup
from AutoSequencerV2.raceCommandGroup import RaceCommandGroup
from AutoSequencerV2.builtInCommands.waitCommand import WaitCommand
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup
from Autonomous.commands.drivePathCommand import DrivePathCommand
from AutoSequencerV2.mode import Mode
from Autonomous.commands.intakeCommand import IntakeCommand
from Autonomous.commands.speakerShootCommand import SpeakerShootCommand


# Just drives out of the starting zone. That's all.
class scoreTwo(Mode):
    def __init__(self):
        Mode.__init__(self, f"Score Two")
        self.pathCmd = DrivePathCommand("scoreTwo")
        self.intake = IntakeCommand()
        self.shoot = SpeakerShootCommand()
        self.wait = WaitCommand(0)
    
        self.intakeCommandGroup = RaceCommandGroup([self.pathCmd, self.intake])
        self.shootCommandGroup = SequentialCommandGroup([self.wait, self.shoot])
        
    def getCmdGroup(self):
        return self.shootCommandGroup.andThen(self.intakeCommandGroup).andThen(self.shootCommandGroup)

    def getInitialDrivetrainPose(self):
        # Use the path command to specify the starting pose
        return self.pathCmd.path.getInitialPose()
