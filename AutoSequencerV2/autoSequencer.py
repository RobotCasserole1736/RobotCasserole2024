from wpimath.geometry import Pose2d
from wpilib import DriverStation
from AutoSequencerV2.modeList import ModeList
from AutoSequencerV2.builtInModes.doNothingMode import DoNothingMode
from AutoSequencerV2.builtInModes.waitMode import WaitMode
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup
from Autonomous.modes.scoreLeaveA import ScoreLeaveA
from Autonomous.modes.scoreLeaveB import ScoreLeaveB
from Autonomous.modes.scoreLeaveC import ScoreLeaveC
from Autonomous.modes.driveOut import DriveOut
from Autonomous.modes.scoreThreeB21 import ScoreThreeB21
from Autonomous.modes.scoreThreeB23 import ScoreThreeB23
from Autonomous.modes.scoreTwoA1 import ScoreTwoA1
from Autonomous.modes.scoreTwoB2 import ScoreTwoB2
from Autonomous.modes.scoreTwoC3 import ScoreTwoC3
from Autonomous.modes.justShoot import justShoot
from Autonomous.modes.scoreTwoC6 import ScoreTwoC6
from Autonomous.modes.scoreTwoA4 import ScoreTwoA4
from Autonomous.modes.scoreTwoC8 import ScoreTwoC8
from Autonomous.modes.intakeTest import IntakeTest
from utils.singleton import Singleton
from utils.allianceTransformUtils import onRed
from utils.allianceTransformUtils import transform

class AutoSequencer(metaclass=Singleton):
    """Top-level implementation of the AutoSequencer"""

    def __init__(self):
        # Have different delay modes for delaying the start of autonomous
        self.delayModeList = ModeList("Delay")
        self.delayModeList.addMode(WaitMode(0.0))
        self.delayModeList.addMode(WaitMode(3.0))
        self.delayModeList.addMode(WaitMode(6.0))
        self.delayModeList.addMode(WaitMode(9.0))

        # Create a list of every autonomous mode we want
        self.mainModeList = ModeList("Main")
        self.mainModeList.addMode(DoNothingMode())
        self.mainModeList.addMode(DriveOut())
        self.mainModeList.addMode(justShoot())
        #self.mainModeList.addMode(IntakeTest())
        self.mainModeList.addMode(ScoreLeaveA())
        self.mainModeList.addMode(ScoreLeaveB())
        self.mainModeList.addMode(ScoreLeaveC())
        self.mainModeList.addMode(ScoreTwoA1())
        self.mainModeList.addMode(ScoreTwoB2())
        self.mainModeList.addMode(ScoreTwoC3())
        self.mainModeList.addMode(ScoreTwoA4())
        self.mainModeList.addMode(ScoreTwoC6())
        self.mainModeList.addMode(ScoreTwoC8())

        self.mainModeList.addMode(ScoreThreeB21())
        self.mainModeList.addMode(ScoreThreeB23())
    
        
        


        self.topLevelCmdGroup = SequentialCommandGroup()
        self.startPose = Pose2d()

        # Alliance changes require us to re-plan autonomous
        # This variable is used to help track when alliance changes
        self._prevOnRed = onRed()

        self.updateMode(force=True)  # Ensure we load the auto sequencer at least once.

    # Returns true if the alliance has changed since the last call
    def _allianceChanged(self):
        curRed = onRed()
        retVal = curRed != self._prevOnRed
        self._prevOnRed = curRed
        return retVal

    def addMode(self, newMode):
        self.mainModeList.addMode(newMode)

    # Call this periodically while disabled to keep the dashboard updated
    # and, when things change, re-init modes
    def updateMode(self, force=False):
        mainChanged = self.mainModeList.updateMode()
        delayChanged = self.delayModeList.updateMode()
        if mainChanged or delayChanged or force or self._allianceChanged():
            mainMode = self.mainModeList.getCurMode()
            mainMode.__init__()
            delayMode = self.delayModeList.getCurMode()
            self.topLevelCmdGroup = delayMode.getCmdGroup().andThen(
                mainMode.getCmdGroup()
            )
            self.startPose = transform(mainMode.getInitialDrivetrainPose())
            print(
                f"[Auto] New Modes Selected: {DriverStation.getAlliance()} {delayMode.getName()}, {mainMode.getName()}"
            )

    # Call this once during autonmous init to init the current command sequence
    def initialize(self):
        print("[Auto] Starting Sequencer")
        self.topLevelCmdGroup.initialize()

    def update(self):
        self.topLevelCmdGroup.execute()

    def end(self):
        self.topLevelCmdGroup.end(True)
        print("[Auto] Sequencer Stopped")

    def getMainModeList(self):
        return self.mainModeList.getNames()

    def getMainModeNTTableName(self):
        return self.mainModeList.getModeTopicBase()

    def getDelayModeList(self):
        return self.delayModeList.getNames()

    def getDelayModeNTTableName(self):
        return self.delayModeList.getModeTopicBase()

    def getStartingPose(self):
        return self.startPose
