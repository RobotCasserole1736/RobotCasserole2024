from AutoSequencerV2.parallelCommandGroup import ParallelCommandGroup
from AutoSequencerV2.builtInCommands.waitCommand import WaitCommand
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup
from Autonomous.commands.drivePathCommand import DrivePathCommand
from AutoSequencerV2.mode import Mode
from Autonomous.commands.driveForwardSlowCommand import DriveForwardSlowCommand
from Autonomous.commands.intakeCommand import IntakeCommand
from Autonomous.commands.speakerShootCommand import SpeakerShootCommand

class ScoreTwoA(Mode):
    def __init__(self):
        Mode.__init__(self, f"Score 2 - Zone A")
        self.pathCmd = DrivePathCommand("scoreTwoA.1")
        self.intake = IntakeCommand()
        self.shoot = SpeakerShootCommand()
        self.shoot2 = SpeakerShootCommand()
        self.wait = WaitCommand(1)
        self.wait2 = WaitCommand(1)
        self.wait3 = WaitCommand(1)

        self.intakeCommandGroup = ParallelCommandGroup([self.pathCmd, self.intake])
        self.shootCommandGroup = SequentialCommandGroup([self.shoot, self.wait])
        self.shootCommandGroup2 = SequentialCommandGroup([self.shoot2, self.wait3])

    def getCmdGroup(self):
        return self.shootCommandGroup.andThen(self.intakeCommandGroup).\
            andThen(self.shootCommandGroup2)

    def getInitialDrivetrainPose(self):
        # Use the path command to specify the starting pose
        return self.pathCmd.path.getInitialPose()