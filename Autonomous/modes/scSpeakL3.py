from AutoSequencerV2.mode import Mode
from AutoSequencerV2.parallelCommandGroup import ParallelCommandGroup
from AutoSequencerV2.raceCommandGroup import RaceCommandGroup
from Autonomous.commands.drivePathCommand import DrivePathCommand
from Autonomous.commands.intakeCommand import IntakeCommand
from Autonomous.commands.speakerShootCommand import SpeakerShootCommand
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup

class ScSpeakL3(Mode):
    def __init__(self):
        Mode.__init__(self, f"Sc Speak L 3")
        self.pathCmd1 = DrivePathCommand("DriveOut3")
        self.shoot = SpeakerShootCommand()
        self.firstPartList = [self.shoot, self.pathCmd1]
        self.firstPartList2 = SequentialCommandGroup(self.firstPartList)

    
    def getCmdGroup(self):
        # Return shoot, then path command
        return self.firstPartList2
    
    def getInitialDrivetrainPose(self):
        # Use the path command to specify the starting pose
        return self.pathCmd1.path.getInitialPose()
