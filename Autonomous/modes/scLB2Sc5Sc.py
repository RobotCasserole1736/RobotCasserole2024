from AutoSequencerV2.parallelCommandGroup import ParallelCommandGroup
from AutoSequencerV2.raceCommandGroup import RaceCommandGroup
from AutoSequencerV2.builtInCommands.waitCommand import WaitCommand
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup
from Autonomous.commands.drivePathCommand import DrivePathCommand
from AutoSequencerV2.mode import Mode
from Autonomous.commands.intakeCommand import IntakeCommand
from Autonomous.commands.speakerShootCommand import SpeakerShootCommand
from Autonomous.commands.retractCommand import RetractCommand


class ScLB2Sc5Sc(Mode):
    def __init__(self):
        Mode.__init__(self, f"Score 3 - Zone 2")
        self.pathCmd1 = DrivePathCommand("Speaker_primary_path.1")
        self.pathCmd2 = DrivePathCommand("Speaker_primary_path.2")
        self.pathCmd3 = DrivePathCommand("Speaker_primary_path.3")
        self.intake1 = IntakeCommand()
        self.intake2 = IntakeCommand()
        self.shoot = SpeakerShootCommand()
        self.shoot2 = SpeakerShootCommand()
        self.shoot3 = SpeakerShootCommand()
        self.wait = WaitCommand(1)
        self.wait2 = WaitCommand(1)
        self.wait3 = WaitCommand(1)
        self.wait4 = WaitCommand(1)

        self.intakeCommandGroup1 = ParallelCommandGroup([self.pathCmd1, self.intake1])
        self.intakeCommandGroup2 = ParallelCommandGroup([self.pathCmd3, self.intake2])
        self.justDriveCommandGroup = ParallelCommandGroup([self.pathCmd2, self.wait4])
        self.shootCommandGroup1 = SequentialCommandGroup([self.shoot, self.wait])
        self.shootCommandGroup2 = SequentialCommandGroup([self.shoot2, self.wait2])
        self.shootCommandGroup3 = SequentialCommandGroup([self.shoot3, self.wait3])

    def getCmdGroup(self):
        return self.shootCommandGroup1.andThen(self.intakeCommandGroup1).andThen(self.shootCommandGroup2).andThen(
            self.justDriveCommandGroup).andThen(self.intakeCommandGroup2).andThen(self.shootCommandGroup3)
                

    def getInitialDrivetrainPose(self):
        # Use the path command to specify the starting pose
        return self.pathCmd1.path.getInitialPose()