from AutoSequencerV2.mode import Mode
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup
from AutoSequencerV2.parallelCommandGroup import ParallelCommandGroup
from Autonomous.commands.drivePathCommand import DrivePathCommand
from Autonomous.commands.intakeCommand import IntakeCommand
from Autonomous.commands.speakerShootCommand import SpeakerShootCommand

class ScSpeakLP1(Mode):
    def __init__(self):
        Mode.__init__(self, f"Sc Speak L P 1")
        self.pathCmd1 = DrivePathCommand("DriveOut1.1")
        self.pathCmd2 = DrivePathCommand("DriveOut1.2")
        self.shoot = SpeakerShootCommand()
        self.intake = IntakeCommand()
        self.firstCommandList = [self.shoot, self.pathCmd1]
        self.firstCommandList2 = SequentialCommandGroup(self.firstCommandList)

        self.secondList = [self.intake, self.pathCmd2]
        self.secondList2 = ParallelCommandGroup(self.secondList)
    
    def getCmdGroup(self):
        # Return shoot, then path command
        return self.firstCommandList2.andThen(self.secondList2)

    def getInitialDrivetrainPose(self):
        # Use the path command to specify the starting pose
        return self.pathCmd1.path.getInitialPose()
