# Priorities
# 1. Read the rest of the documentation for ToF
# 2. Take a look at SparkMax stuff
# 3. Ask about playing with fusion and how to implement and if did classes correct
# 4. Get information from Operator control block on architecture

# Resources: https://robotpy.readthedocs.io/projects/pwfusion/en/latest/playingwithfusion/TimeOfFlight.html

# Imports
from playingwithfusion import TimeOfFlight
from utils.calibration import Calibration
from utils import constants, faults
from utils.units import RPM2RadPerSec, m2in
from wrappers.wrapperedSparkMax import WrapperedSparkMax


class GamePieceHandling:
    def __init__(self):
        # Shooter Motors
        self.shooterMotor1 = WrapperedSparkMax(
            constants.SHOOTER_MOTOR1_CANID, "ShooterMotor1"
        )
        self.shooterMotor2 = WrapperedSparkMax(
            constants.SHOOTER_MOTOR2_CANID, "ShooterMotor2"
        )

        # Intake Motors
        self.intakeMotor1 = WrapperedSparkMax(constants.INTAKE_MOTOR1_CANID1, "IntakeMotor1")
        self.intakeMotor2 = WrapperedSparkMax(constants.INTAKE_MOTOR2_CANID2, "IntakeMotor2")

        # Floor Roller Motors
        self.floorRoolerMotor1 = WrapperedSparkMax(
            constants.FLOORROLLER_MOTOR1_CANID, "FloorRollerMotor1"
        )
        self.floorRoolerMotor2 = WrapperedSparkMax(
            constants.FLOORROLLER_MOTOR2_CANID, "FloorRollerMotor2"
        )

        self.tofFault = faults.Fault("Claw TOF Sensor is Disconnected")

        # Shooter Calibrations (PID Controller)
        self.shooterkFCal = Calibration("ShooterkF", 0.00255, "V/RPM")
        self.shooterkPCal = Calibration("ShooterkP", 0)

        # Intake Voltage Calibration
        self.intakeVoltageCal = Calibration("IntakeVoltage", 12, "V")

        # Time of Flight sensor for checking gamepiece present
        self.tofSensor = TimeOfFlight(12)
        self.tofSensor.setRangingMode(TimeOfFlight.RangingMode.kShort, 24)
        self.tofSensor.setRangeOfInterest(6, 6, 10, 10)  # fov for sensor
        self.hasGamePiece = False

        # Calibrations for Gamepiece being absent and present
        self.gamePiecePresentCal = Calibration("NotePresentThresh", 7, "in")
        self.gamePieceAbsentCal = Calibration("NoteAbsentThresh", 11, "in")

        # TOF Disconnected Fault
        self.disconTOFFault = faults.Fault("Singer TOF Sensor is Disconnected")

    def activeShooter(self, desVel):
        self.shooterMotor1.setVelCmd(RPM2RadPerSec(desVel))  # ArbFF default 0
        self.shooterMotor1.setVelCmd(RPM2RadPerSec(desVel))  # ArbFF defualt 0

    def activeIntake(self):
        self.intakeMotor1.setVoltage(self.intakeVoltageCal)
        self.intakeMotor2.setVoltage(self.intakeVoltageCal)

    def activeFloorRoller(self):
        self.floorRoolerMotor1.setVoltage(self.intakeVoltageCal)
        self.floorRoolerMotor2.setVoltage(self.intakeVoltageCal)

    def update(self):
        gamepieceDistSensorMeas = m2in(self.tofSensor.getRange() / 1000.0)
        self.disconTOFFault.set(self.tofSensor.getFirmwareVersion() == 0)

        if gamepieceDistSensorMeas < self.gamePiecePresentCal.get():
            self.hasGamePiece = True
        elif gamepieceDistSensorMeas > self.gamePieceAbsentCal.get():
            self.hasGamePiece = False
        else:
            pass
