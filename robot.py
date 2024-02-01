import sys
import wpilib
from Autonomous.modes.driveOut import DriveOut
from dashboard import Dashboard
from gamepieceHandling.gamepieceHandling import GamePieceHandling
from humanInterface.driverInterface import DriverInterface
from humanInterface.ledControl import LEDControl
from prototypeMechanisms.practiceBoardMotor import PracticeBoardMotor
from utils.segmentTimeTracker import SegmentTimeTracker
from utils.signalLogging import SignalWrangler
from utils.calibration import CalibrationWrangler
from utils.faults import FaultWrangler
from utils.crashLogger import CrashLogger
from utils.rioMonitor import RIOMonitor
from utils.singleton import destroyAllSingletonInstances
from webserver.webserver import Webserver
from AutoSequencerV2.autoSequencer import AutoSequencer


class MyRobot(wpilib.TimedRobot):
    #########################################################
    ## Common init/update for all modes
    def robotInit(self):
        # Since we're defining a bunch of new things here, tell pylint
        # to ignore these instantiations in a method.
        # pylint: disable=attribute-defined-outside-init
        remoteRIODebugSupport()

        self.crashLogger = CrashLogger()
        wpilib.LiveWindow.disableAllTelemetry()
        self.webserver = Webserver()


        self.stt = SegmentTimeTracker()

        self.gph = GamePieceHandling()
        self.dInt = DriverInterface()
        self.led = LEDControl()

        self.autoSequencer = AutoSequencer()
        self.autoSequencer.addMode(DriveOut())

        self.dashboard = Dashboard()

        self.rioMonitor = RIOMonitor()

        self.motor = PracticeBoardMotor()

        # Uncomment this and simulate to update the code
        # dependencies graph
        #from codeStructureReportGen import reportGen
        #reportGen.generate(self)

    def robotPeriodic(self):
        self.stt.start()
        self.crashLogger.update()

        self.motor.update()

        SignalWrangler().publishPeriodic()
        CalibrationWrangler().update()
        FaultWrangler().update()
        self.stt.end()

    #########################################################
    ## Autonomous-Specific init and update
    def autonomousInit(self):
        # Start up the autonomous sequencer
        self.autoSequencer.initiaize()

    def autonomousPeriodic(self):
        self.autoSequencer.update()

    def autonomousExit(self):
        self.autoSequencer.end()

    #########################################################
    ## Teleop-Specific init and update
    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        self.dInt.update()

        self.motor.setCmd(
            self.dInt.intakeCmd,
            self.dInt.ejectCmd,
        )

        self.gph.update()
        self.led.setSpeakerAutoAlignActive(self.dInt.autoAlignCmd)
        self.led.setNoteInIntake(self.gph.hasGamePiece)
        self.led.update()

    #########################################################
    ## Disabled-Specific init and update
    def disabledPeriodic(self):
        self.autoSequencer.updateMode()

    #########################################################
    ## Test-Specific init and update
    def testInit(self):
        # Induce a crash
        oopsie = 5 / 0.0  # pylint: disable=unused-variable

    #########################################################
    ## Cleanup
    def endCompetition(self):
        self.rioMonitor.stopThreads()
        destroyAllSingletonInstances()
        super().endCompetition()


def remoteRIODebugSupport():
    if __debug__ and "run" in sys.argv:
        print("Starting Remote Debug Support....")
        try:
            import debugpy # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError:
            pass
        else:
            debugpy.listen(("0.0.0.0", 5678))
            debugpy.wait_for_client()
