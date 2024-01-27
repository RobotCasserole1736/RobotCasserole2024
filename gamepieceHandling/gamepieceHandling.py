# Priorities
# 1. Read the rest of the documentation for ToF
# 2. Take a look at SparkMax stuff
# 3. Ask about playing with fusion and how to implement and if did classes correct
# 4. Get information from Operator control block on architecture

# Resources: https://robotpy.readthedocs.io/projects/pwfusion/en/latest/playingwithfusion/TimeOfFlight.html

# Imports
from wpilib import PWMSparkMax
from utils.calibration import Calibration
from utils import constants, faults
from utils.units import RPM2RadPerSec, m2in
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from playingwithfusion import TimeOfFlight


class GamePieceHandling:
    def __init__(self):
        # Shooter Motors
        self.Shooter1 = WrapperedSparkMax(
            constants.SHOOTER_MOTOR1_CANID, "ShooterMotor1"
        )
        self.Shooter2 = WrapperedSparkMax(
            constants.SHOOTER_MOTOR2_CANID, "ShooterMotor2"
        )

        # Intake Motors
        self.Intake1 = WrapperedSparkMax(constants.INTAKE_MOTOR1_CANID1, "IntakeMotor1")
        self.Intake2 = WrapperedSparkMax(constants.INTAKE_MOTOR2_CANID2, "IntakeMotor2")

        # Floor Roller Motors
        self.FloorRoller1 = WrapperedSparkMax(
            constants.FlOORROLLER_MOTOR1_CANID, "FloorRollerMotor1"
        )
        self.FloorRoller2 = WrapperedSparkMax(
            constants.FLOORROLLER_MOTOR2_CANID, "FloorRollerMotor2"
        )

        self.tofFault = faults.Fault("Claw TOF Sensor is Disconnected")

        # Shooter Calibrations (PID Controller)
        self.ShooterkF = Calibration("ShooterkF", 0.00255, "V/RPM")
        self.ShooterkP = Calibration("ShooterkP", 0)

        # Intake Voltage Calibration
        self.IntakeVoltage = Calibration("IntakeVoltage", 12, "V")

        # Time of Flight sensor
        self.ToFSensor = TimeOfFlight(16)
        self.ToFSensor.setRangingMode(TimeOfFlight.RangingMode.kShort, 24)
        self.ToFSensor.setRangeOfInterest(6, 6, 10, 10)  # fov for sensor
        self.hasGamePiece = False

        # Calibrations for Gamepiece being absent and present
        self.GamePiecePresent = Calibration("NotePresentThresh", 7, "in")
        self.GamePieceAbsent = Calibration("NoteAbsentThresh", 11, "in")

        # TOF Disconnected Fault
        self.disconTOFFault = faults.Fault("Singer TOF Sensor is Disconnected")

    def ActiveShooter(self, desVel):
        self.Shooter1.setVelCmd(RPM2RadPerSec(desVel))  # ArbFF default 0
        self.Shooter1.setVelCmd(RPM2RadPerSec(desVel))  # ArbFF defualt 0

    def ActiveIntake(self):
        self.Intake1.setVoltage(self.IntakeVoltage)
        self.Intake2.setVoltage(self.IntakeVoltage)

    def ActiveFloorRoller(self):
        self.FloorRoller1.setVoltage(self.IntakeVoltage)
        self.FloorRoller2.setVoltage(self.IntakeVoltage)

    def update(self):
        gamepieceDistSensorMeas = m2in(self.ToFSensor.getRange() / 1000.0)
        self.disconTOFFault.set(self.ToFSensor.getFirmwareVersion() == 0)

        if gamepieceDistSensorMeas < self.GamePiecePresent.get():
            self.hasGamePiece = True
        elif gamepieceDistSensorMeas > self.GamePieceAbsent.get():
            self.hasGamePiece = False
        else:
            pass
