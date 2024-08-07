import sys
import wpilib
from dashboard import Dashboard
from drivetrain.controlStrategies.autoDrive import AutoDrive
from drivetrain.controlStrategies.trajectory import Trajectory
from drivetrain.drivetrainCommand import DrivetrainCommand
from drivetrain.drivetrainControl import DrivetrainControl
from pieceHandling.gamepieceHandling import GamePieceHandling
from humanInterface.operatorInterface import OperatorInterface
from humanInterface.driverInterface import DriverInterface
from humanInterface.ledControl import LEDControl
from singerMovement.carriageControl import CarriageControl, CarriageControlCmd
from singerMovement.tunerAngleControl import TunerAngleControl
from utils.segmentTimeTracker import SegmentTimeTracker
from utils.signalLogging import SignalWrangler
from utils.calibration import CalibrationWrangler
from utils.faults import FaultWrangler
from utils.crashLogger import CrashLogger
from utils.rioMonitor import RIOMonitor
from utils.singleton import destroyAllSingletonInstances
from utils.powerMonitor import PowerMonitor
from webserver.webserver import Webserver
from AutoSequencerV2.autoSequencer import AutoSequencer
from climbControl.climberControl import ClimberControl
from utils.powerMonitor import PowerMonitor

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
        
        #self.cc = CarriageControl()
        
        self.tc = TunerAngleControl()

        self.oInt = OperatorInterface()
        self.dInt = DriverInterface()

        self.climbCtrl = ClimberControl()

        self.gph = GamePieceHandling()

        self.ledCtrl = LEDControl()

        self.autoSequencer = AutoSequencer()

        self.dashboard = Dashboard()

        self.rioMonitor = RIOMonitor()
        self.pwrMon = PowerMonitor()

        # Normal robot code updates every 20ms, but not everything needs to be that fast.
        # Register slower-update periodic functions
        self.addPeriodic(self.ledCtrl.update, self.ledCtrl.sampleTime, 0.0)
        self.addPeriodic(self.dashboard.update, 0.2, 0.0)
        self.addPeriodic(self.pwrMon.update, 0.2, 0.0)
        self.addPeriodic(self.crashLogger.update, 1.0, 0.0)
        self.addPeriodic(CalibrationWrangler().update, 0.5, 0.0)
        self.addPeriodic(FaultWrangler().update, 0.2, 0.0)

        # One-time init of carriage position from the absolute sensors
        #self.cc.initFromAbsoluteSensors()

    def robotPeriodic(self):
        self.stt.start()

        self.driveTrain.update()

        self.climbCtrl.update()
        
        #self.cc.update(useFuncGen=self.isTestEnabled())
        
        self.tc.update()

        self.gph.update()

        self.stt.end()

    #########################################################
    ## Autonomous-Specific init and update
    def autonomousInit(self):

        # Start up the autonomous sequencer
        self.autoSequencer.initialize()

        # Use the autonomous rouines starting pose to init the pose estimator
        self.driveTrain.poseEst.setKnownPose(self.autoSequencer.getStartingPose())

        # TODO - remove these if we're going to attmept amp shots in auto
        self.gph.setIsAmpShot(False)
        self.tc.setIsAmpShot(False)


    def autonomousPeriodic(self):
        SignalWrangler().markLoopStart()

        self.autoSequencer.update()

        # Operators cannot control in autonomous
        self.driveTrain.setManualCmd(DrivetrainCommand())

        self.climbCtrl.ctrlWinch(0.0)

    def autonomousExit(self):
        self.autoSequencer.end()

    #########################################################
    ## Teleop-Specific init and update
    def teleopInit(self):
        pass

    def teleopPeriodic(self):

        SignalWrangler().markLoopStart()
        self.oInt.update()
        self.dInt.update()

        ampShot = self.oInt.getTunerPosCmd()
        self.tc.setIsAmpShot(ampShot)
        self.gph.setIsAmpShot(ampShot)

        self.driveTrain.setManualCmd(self.dInt.getCmd())
        AutoDrive().setSpeakerAutoAlignCmd(self.oInt.getSpeakerAutoAlignCmd())

        if self.dInt.getGyroResetCmd():
            self.driveTrain.resetGyro()

        # Gamepiece handling input
        self.gph.setInput(
            self.oInt.getSingerSpoolUpCmd(),
            self.oInt.getSingerIntakeCmd(),
            self.oInt.getSingerEjectCmd(),
            self.oInt.getSingerShootCmd()
        )

        # self.ledCtrl.setSpeakerAutoAlignActive(self.oInt.getSpeakerAutoAlignCmd())
        self.ledCtrl.setNoteInIntake(self.gph.hasGamePiece)
        self.ledCtrl.update()

        # No trajectory in Teleop
        Trajectory().setCmd(None)
        self.driveTrain.poseEst.telemetry.setTrajectory(None)

        self.climbCtrl.ctrlWinch(self.dInt.getWinchCmd())

    #########################################################
    ## Disabled-Specific init and update
    def disabledPeriodic(self):
        SignalWrangler().markLoopStart()
        self.autoSequencer.updateMode()
        Trajectory().trajCtrl.updateCals()

    def disabledInit(self):
        self.oInt.update()
        self.dInt.update()
        self.autoSequencer.updateMode(True)

    #########################################################
    ## Test-Specific init and update
    def testInit(self):
        wpilib.LiveWindow.setEnabled(False)
        #self.cc.onEnable(True) # init the function generator

    def testPeriodic(self):
        SignalWrangler().markLoopStart()
        # Nothing else to do, main update does all the heavy lifting

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