from AutoSequencerV2.parallelCommandGroup import ParallelCommandGroup
from AutoSequencerV2.raceCommandGroup import RaceCommandGroup
from AutoSequencerV2.builtInCommands.waitCommand import WaitCommand
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup
from Autonomous.commands.drivePathCommand import DrivePathCommand
from AutoSequencerV2.mode import Mode
from Autonomous.commands.intakeCommand import IntakeCommand
from Autonomous.commands.speakerShootCommand import SpeakerShootCommand
from Autonomous.commands.retractCommand import RetractCommand

# Just drives out of the starting zone. That's all.
class ScoreThreeB21(Mode):
    def __init__(self):
        Mode.__init__(self, f"Score Three B 21")
        
        self.pathCmd = DrivePathCommand("ScoreTwoB2")
        self.pathCmd2 = DrivePathCommand("ScoreThreeB21")
        
        self.intake = IntakeCommand()
        self.intake.maxDuration(3)
        self.intake2 = IntakeCommand()
        self.intake2.maxDuration(4)
        
        self.shoot = SpeakerShootCommand()
        self.shoot2 = SpeakerShootCommand()
        self.shoot3 = SpeakerShootCommand()
        
        self.wait = WaitCommand(0)
     

        self.intakeDriveCommandGroup = ParallelCommandGroup([self.pathCmd, self.intake])
        self.shootCommandGroup = SequentialCommandGroup([self.shoot, self.wait])
        self.shootCommandGroup2 = SequentialCommandGroup([self.shoot2, self.wait])
        
        self.intakeDriveCommandGroup2 = ParallelCommandGroup([self.pathCmd2, self.intake2])
        self.shootCommandGroup3 = SequentialCommandGroup([self.shoot3, self.wait])

    def getCmdGroup(self):
        return self.shootCommandGroup.andThen(self.intakeDriveCommandGroup).andThen(self.shootCommandGroup2).andThen(self.intakeDriveCommandGroup2).andThen(self.shootCommandGroup3)
       
    def getInitialDrivetrainPose(self):
        # Use the path command to specify the starting pose.
        return self.pathCmd.path.getInitialPose()