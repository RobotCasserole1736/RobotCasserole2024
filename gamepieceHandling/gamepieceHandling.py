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
        self.shooterMotorLeft = WrapperedSparkMax(
            constants.SHOOTER_MOTOR_LEFT_CANID, "ShooterMotorLeft"
        )
        self.shooterMotorRight = WrapperedSparkMax(
            constants.SHOOTER_MOTOR_RIGHT_CANID, "ShooterMotorRight"
        )

        # Intake Motors
        self.intakeMotorUpper = WrapperedSparkMax(constants.INTAKE_MOTOR_UPPER_CANID1, "IntakeMotorUpper")
        self.intakeMotorLower = WrapperedSparkMax(constants.INTAKE_MOTOR_LOWER_CANID2, "IntakeMotorLower")

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

        # Time of Flight sensor
        self.tofSensor = TimeOfFlight(16)
        self.tofSensor.setRangingMode(TimeOfFlight.RangingMode.kShort, 24)
        self.tofSensor.setRangeOfInterest(6, 6, 10, 10)  # fov for sensor
        self.hasGamePiece = False

        # Calibrations for Gamepiece being absent and present
        self.gamePiecePresentCal = Calibration("NotePresentThresh", 7, "in")
        self.gamePieceAbsentCal = Calibration("NoteAbsentThresh", 11, "in")

        # TOF Disconnected Fault
        self.disconTOFFault = faults.Fault("Singer TOF Sensor is Disconnected")

    def activeShooter(self, desVel):
        self.shooterMotorLeft.setVelCmd(RPM2RadPerSec(desVel))  # ArbFF default 0
        self.shooterMotorRight.setVelCmd(RPM2RadPerSec(desVel))  # ArbFF defualt 0

    def activeIntake(self,intakeCmd,ejectCmd):
        if intakeCmd == True and ejectCmd == False:
            print("Intaking")
            self.intakeMotorUpper.setVoltage(-1 * self.intakeVoltageCal.get())
            self.intakeMotorLower.setVoltage(-1 * self.intakeVoltageCal.get())
        elif intakeCmd == False and ejectCmd == True:
            print("Eject")
            self.intakeMotorUpper.setVoltage(self.intakeVoltageCal.get())
            self.intakeMotorLower.setVoltage(self.intakeVoltageCal.get())
        elif intakeCmd == False and ejectCmd == False:
            print("No intake cmd")
            self.intakeMotorUpper.setVoltage(0)
            self.intakeMotorLower.setVoltage(0)

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

    def setInput(self, SingerShooterBoolean, SingerIntakeBoolean, SingerEjectBoolean):
        self.activeIntake(SingerIntakeBoolean,SingerEjectBoolean)

        if SingerShooterBoolean:
            self.activeShooter(self.shooterkFCal.get())