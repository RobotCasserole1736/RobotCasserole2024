import sys
import wpilib
from Autonomous.modes.driveOut import DriveOut
from Autonomous.modes.noteThief import NoteThief
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
from utils.segmentTimeTracker import SegmentTimeTracker
from utils.signalLogging import SignalWrangler
from utils.calibration import CalibrationWrangler
from utils.faults import FaultWrangler
from utils.crashLogger import CrashLogger
from utils.rioMonitor import RIOMonitor
from utils.singleton import destroyAllSingletonInstances
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

        self.oInt = OperatorInterface()
        self.dInt = DriverInterface()

        self.climbCtrl = ClimberControl() 

        self.carriageControl = CarriageControl()
        self.gph = GamePieceHandling()

        self.ledCtrl = LEDControl()

        self.autoSequencer = AutoSequencer()
        self.autoSequencer.addMode(DriveOut())
        self.autoSequencer.addMode(NoteThief())

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

    def robotPeriodic(self):
        self.stt.start()

        self.driveTrain.update()

        self.climbCtrl.update()

        self.gph.update()

        self.carriageControl.update()

        self.stt.end()

    #########################################################
    ## Autonomous-Specific init and update
    def autonomousInit(self):

        # Start up the autonomous sequencer
        self.autoSequencer.initiaize()

        # Use the autonomous rouines starting pose to init the pose estimator
        self.driveTrain.poseEst.setKnownPose(self.autoSequencer.getStartingPose())

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

        self.driveTrain.setManualCmd(self.dInt.getCmd())
        AutoDrive().setSpeakerAutoAlignCmd(self.oInt.getSpeakerAutoAlignCmd())
        AutoDrive().setAmpAutoAlignCmd(self.oInt.getCarriageAmpPosCmd())

        if self.dInt.getGyroResetCmd():
            self.driveTrain.resetGyro()

        # Map operator command to carriage control command
        if(self.oInt.getCarriageAmpPosCmd()):
            self.carriageControl.setPositionCmd(CarriageControlCmd.AMP)
        elif(self.oInt.getCarriageIntakePosCmd()):
            self.carriageControl.setPositionCmd(CarriageControlCmd.INTAKE)
        elif(self.oInt.getCarriageTrapPosCmd()):
            self.carriageControl.setPositionCmd(CarriageControlCmd.TRAP)
        elif(self.oInt.getSpeakerAutoAlignCmd()):
            self.carriageControl.setPositionCmd(CarriageControlCmd.AUTO_ALIGN)
        else:
            self.carriageControl.setPositionCmd(CarriageControlCmd.HOLD)

        
        # Gamepiece handling input
        self.gph.setInput(
            self.oInt.getSingerShootCmd(),
            self.oInt.getSingerIntakeCmd(),
            self.oInt.getSingerEjectCmd()
        )

        self.ledCtrl.setSpeakerAutoAlignActive(self.oInt.getSpeakerAutoAlignCmd())
        self.ledCtrl.setNoteInIntake(self.gph.hasGamePiece)
        self.ledCtrl.update()
        
        # No trajectory in Teleop
        Trajectory().setCmd(None)
        self.driveTrain.poseEst.telemetry.setTrajectory(None)

        self.climbCtrl.ctrlWinch(self.dInt.velWinchCmd)


    #########################################################
    ## Disabled-Specific init and update
    def disabledPeriodic(self):
        SignalWrangler().markLoopStart()
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
