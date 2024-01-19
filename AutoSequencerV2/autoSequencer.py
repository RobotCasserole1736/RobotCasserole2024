from wpimath.geometry import Pose2d
from AutoSequencerV2.modeList import ModeList
from AutoSequencerV2.builtInModes.doNothingMode import DoNothingMode
from AutoSequencerV2.builtInModes.waitMode import WaitMode
from AutoSequencerV2.sequentialCommandGroup import SequentialCommandGroup
from utils.singleton import Singleton


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

        self.topLevelCmdGroup = SequentialCommandGroup()
        self.startPose = Pose2d()

        self.updateMode(force=True)  # Ensure we load the auto sequencer at least once.

    def addMode(self, newMode):
        self.mainModeList.addMode(newMode)

    # Call this periodically while disabled to keep the dashboard updated
    # and, when things change, re-init modes
    def updateMode(self, force=False):
        mainChanged = self.mainModeList.updateMode()
        delayChanged = self.delayModeList.updateMode()
        if mainChanged or delayChanged or force:
            mainMode = self.mainModeList.getCurMode()
            delayMode = self.delayModeList.getCurMode()
            self.topLevelCmdGroup = delayMode.getCmdGroup().andThen(
                mainMode.getCmdGroup()
            )
            self.startPose = mainMode.getInitialDrivetrainPose()
            print(
                f"[Auto] New Modes Selected: {delayMode.getName()}, {mainMode.getName()}"
            )

    # Call this once during autonmous init to init the current command sequence
    def initiaize(self):
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
