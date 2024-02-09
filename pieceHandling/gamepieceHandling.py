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
        # Booleans
        self.shooterOn = False
        self.intakeOn = False
        self.ejectOn = False

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
        self.shooterVel = Calibration("Shooter Velocity", 4700, "RPM")

        self.shooterMotorLeft.setPID(self.shooterkPCal.get(),0,self.shooterkFCal.get())
        self.shooterMotorRight.setPID(self.shooterkPCal.get(),0,self.shooterkFCal.get())

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

    def activeShooter(self):
        desVel = RPM2RadPerSec(self.shooterVel)
        self.shooterMotorLeft.setVelCmd(desVel,desVel*self.shooterkFCal.get())
        self.shooterMotorRight.setVelCmd(desVel,desVel*self.shooterkFCal.get())

    def activeIntake(self):
        self.intakeMotorUpper.setVoltage(self.intakeVoltageCal.get())
        self.intakeMotorLower.setVoltage(self.intakeVoltageCal.get())

    def activeFloorRoller(self):
        self.floorRoolerMotor1.setVoltage(self.intakeVoltageCal.get())
        self.floorRoolerMotor2.setVoltage(self.intakeVoltageCal.get())

    def update(self):
        # Update PID Gains if needed
        if self.shooterkPCal.isChanged() or self.shooterkFCal.isChanged():
            self.shooterMotorLeft.setPID(self.shooterkPCal.get(),0,self.shooterkFCal.get())
            self.shooterMotorRight.setPID(self.shooterkPCal.get(),0,self.shooterkFCal.get())

        # TOF Sensor Update
        gamepieceDistSensorMeas = m2in(self.tofSensor.getRange() / 1000.0)
        self.disconTOFFault.set(self.tofSensor.getFirmwareVersion() == 0)

        if gamepieceDistSensorMeas < self.gamePiecePresentCal.get():
            self.hasGamePiece = True
        elif gamepieceDistSensorMeas > self.gamePieceAbsentCal.get():
            self.hasGamePiece = False
        else:
            pass

        # Gamepiece Handling
        if self.intakeOn and not self.hasGamePiece:
            self.activeIntake()
            self.activeFloorRoller()
        elif self.shooterOn:
            self.activeShooter()
            curShooterVel = max(self.shooterMotorLeft.getMotorVelocityRadPerSec(),self.shooterMotorRight.getMotorVelocityRadPerSec())
            if abs(RPM2RadPerSec(self.shooterVel) - curShooterVel) < 0.05:
                self.activeIntake()

    def setInput(self, SingerShooterBoolean, SingerIntakeBoolean, SingerEjectBoolean):
        self.shooterOn = SingerShooterBoolean
        self.intakeOn = SingerIntakeBoolean
        self.ejectOn = SingerEjectBoolean