import wpilib
from AutoSequencerV2.autoSequencer import AutoSequencer
from dashboardWidgets.autoChooser import AutoChooser
from dashboardWidgets.swerveState import SwerveState
from dashboardWidgets.icon import Icon
from dashboardWidgets.text import Text
from utils.faults import FaultWrangler
from utils.signalLogging import log
from webserver.webserver import Webserver

class Dashboard:
    def __init__(self):

        webServer = Webserver()

        webServer.addDashboardWidget(Icon(15, 60, "/SmartDashboard/isRedIconState", "#FF0000", "allianceRed"))
        webServer.addDashboardWidget(Icon(25, 60, "/SmartDashboard/isBlueIconState", "#0000FF", "allianceBlue"))
        webServer.addDashboardWidget(Icon(35, 60, "/SmartDashboard/PE Vision Targets Seen", "#00FF00", "vision"))
        webServer.addDashboardWidget(Icon(45, 60, "/SmartDashboard/faultIconState", "#FF2200", "warning"))

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
