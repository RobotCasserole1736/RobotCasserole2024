from AutoSequencerV2.mode import Mode
from AutoSequencerV2.raceCommandGroup import RaceCommandGroup
from Autonomous.commands.drivePathCommand import DrivePathCommand
from Autonomous.commands.intakeCommand import IntakeCommand
from Autonomous.commands.speakerShootCommand import SpeakerShootCommand
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup

class ScSpeakL3(Mode):
    def __init__(self):
        Mode.__init__(self, f"Sc Speak L 3")
        self.SequentialCommandGroup = SequentialCommandGroup()
        self.pathCmd = DrivePathCommand("DriveOut3")
        self.intake = IntakeCommand()
        self.shoot = SpeakerShootCommand()
        self.commandList = [self.shoot, self.pathCmd]
        self.commandList2 = SequentialCommandGroup(self.commandList)
        self.extraList = [self.intake, self.shoot]
        self.extraList2 = RaceCommandGroup(self.extraList)
    
    def getCmdGroup(self):
        # Return shoot, then path command
        return self.commandList2.andThen(self.intake)

    def getInitialDrivetrainPose(self):
        # Use the path command to specify the starting pose
        return self.pathCmd.path.getInitialPose()
