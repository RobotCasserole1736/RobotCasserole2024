import sys
import wpilib
from Autonomous.modes.driveOut import DriveOut
from Autonomous.modes.noteThief import NoteThief
from dashboard import Dashboard
from drivetrain.controlStrategies.trajectory import Trajectory
from drivetrain.drivetrainCommand import DrivetrainCommand
from drivetrain.drivetrainControl import DrivetrainControl
from gamepieceHandling.gamepieceHandling import GamePieceHandling
from humanInterface.operatorInterface import OperatorInterface
from humanInterface.driverInterface import DriverInterface
from humanInterface.ledControl import LEDControl
from utils.segmentTimeTracker import SegmentTimeTracker
from utils.signalLogging import SignalWrangler
from utils.calibration import CalibrationWrangler
from utils.faults import FaultWrangler
from utils.crashLogger import CrashLogger
from utils.rioMonitor import RIOMonitor
from utils.singleton import destroyAllSingletonInstances
from webserver.webserver import Webserver
from AutoSequencerV2.autoSequencer import AutoSequencer
from climberControl.climberControl import ClimberControl


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

        self.driveTrain = DrivetrainControl()

        self.stt = SegmentTimeTracker()

        self.oInt = OperatorInterface()
        self.dInt = DriverInterface()

        self.climbCtrl = ClimberControl(
            16
        )  # TODO: is this the right CAN ID? TODO: this is an inconsistent place to define a CAN ID

        self.gph = GamePieceHandling()

        self.ledCtrl = LEDControl()

        self.autoSequencer = AutoSequencer()
        self.autoSequencer.addMode(DriveOut())
        self.autoSequencer.addMode(NoteThief())

        self.dashboard = Dashboard()

        self.rioMonitor = RIOMonitor()

    def robotPeriodic(self):
        self.stt.start()
        self.crashLogger.update()

        self.driveTrain.update()

        self.ledCtrl.update()

        self.climbCtrl.update()

        self.gph.update()

        self.dashboard.update()

        SignalWrangler().publishPeriodic()
        CalibrationWrangler().update()
        FaultWrangler().update()
        self.stt.end()

    #########################################################
    ## Autonomous-Specific init and update
    def autonomousInit(self):
        # Start up the autonomous sequencer
        self.autoSequencer.initiaize()

        # Use the autonomous rouines starting pose to init the pose estimator
        self.driveTrain.poseEst.setKnownPose(self.autoSequencer.getStartingPose())

        self.ledCtrl.setSpeakerAutoAlignActive(True)

    def autonomousPeriodic(self):
        self.autoSequencer.update()

        # Operators cannot control in autonomous
        self.driveTrain.setManualCmd(DrivetrainCommand())

    def autonomousExit(self):
        self.autoSequencer.end()

    #########################################################
    ## Teleop-Specific init and update
    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        self.oInt.update()
        self.dInt.update()

        self.driveTrain.setManualCmd(self.dInt.getCmd())

        if self.dInt.getGyroResetCmd():
            self.driveTrain.resetGyro()

        # No trajectory in Teleop
        Trajectory().setCmd(None)
        self.driveTrain.poseEst.telemetry.setTrajectory(None)

        self.climbCtrl.ctrlWinch(self.dInt.velWinchCmd)

    #########################################################
    ## Disabled-Specific init and update
    def disabledPeriodic(self):
        self.autoSequencer.updateMode()
        Trajectory().trajCtrl.updateCals()

    #########################################################
    ## Test-Specific init and update
    def testInit(self):
        pass

    def testUpdate(self):
        pass

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
            import debugpy  # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError:
            pass
        else:
            debugpy.listen(("0.0.0.0", 5678))
            debugpy.wait_for_client()
