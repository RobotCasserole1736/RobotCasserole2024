import wpilib
import cscore as cs
from cscore import CameraServer
from AutoSequencerV2.autoSequencer import AutoSequencer
from dashboardWidgets.autoChooser import AutoChooser
from dashboardWidgets.swerveState import SwerveState
from dashboardWidgets.icon import Icon
from dashboardWidgets.text import Text
from dashboardWidgets.camera import Camera
from dashboardWidgets.circularGauge import CircularGauge
from utils.faults import FaultWrangler
from utils.signalLogging import log
from humanInterface.operatorInterface import OperatorInterface
from webserver.webserver import Webserver
from pieceHandling.gamepieceHandling import GamePieceHandling


class Dashboard:
    def __init__(self):

        webServer = Webserver()

        webServer.addDashboardWidget(Icon(45, 45, "/SmartDashboard/isRedIconState", "#FF0000", "allianceRed"))
        webServer.addDashboardWidget(Icon(55, 45, "/SmartDashboard/isBlueIconState", "#0000FF", "allianceBlue"))
        webServer.addDashboardWidget(Icon(45, 55, "/SmartDashboard/PE Vision Targets Seen", "#00FF00", "vision"))
        webServer.addDashboardWidget(Icon(55, 55, "/SmartDashboard/faultIconState", "#FF2200", "warning"))
        webServer.addDashboardWidget(Icon(45, 65, "/SmartDashboard/GamepieceIconState", "#00FF00", "newIntakeimg"))
        webServer.addDashboardWidget(Icon(55, 65, "/SmartDashboard/AutoAlignIconState", "#0000FF", "autoAlign"))

        if not wpilib.RobotBase.isSimulation():
            leftCamera = cs.UsbCamera("LEFT_CAM", 0)
            cs.CameraServer.startAutomaticCapture(0)
            cs.CameraServer.getVideo(leftCamera)
            leftCamera.setPath("http://roborio-1736-frc.local:1181")
            webServer.addDashboardWidget(Camera(75, 60, "http://roborio-1736-frc.local:1181/stream.mjpg"))
        

        webServer.addDashboardWidget(
            CircularGauge(10, 55, "/SmartDashboard/ShooterGaugeSpeed", 0, 4700, 0, 4700))

        webServer.addDashboardWidget(Text(50, 75, "/SmartDashboard/faultDescription"))
        webServer.addDashboardWidget(SwerveState(85, 15))
        webServer.addDashboardWidget(
            AutoChooser(
                50,
                10,
                AutoSequencer().getDelayModeNTTableName(),
                AutoSequencer().getDelayModeList(),
            )
        )
        webServer.addDashboardWidget(
            AutoChooser(
                50,
                20,
                AutoSequencer().getMainModeNTTableName(),
                AutoSequencer().getMainModeList(),
            )
        )

    def update(self):
        log("isRedIconState",  
            Icon.kON if wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kRed 
            else Icon.kOFF)
        log("isBlueIconState", 
            Icon.kON if wpilib.DriverStation.getAlliance() == wpilib.DriverStation.Alliance.kBlue 
            else Icon.kOFF)
        log("faultIconState", Icon.kBLINK_FAST if FaultWrangler().hasActiveFaults() else Icon.kOFF)

        log("GamepieceIconState", Icon.kON if OperatorInterface().getSingerIntakeCmd() else Icon.kOFF)

        log("AutoAlignIconState", Icon.kON if OperatorInterface().getSpeakerAutoAlignCmd() else Icon.kOFF)

        log("ShooterGaugeSpeed", GamePieceHandling().getShooterMotorSpeed())
