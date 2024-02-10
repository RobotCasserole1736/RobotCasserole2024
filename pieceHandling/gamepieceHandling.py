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
from utils.singleton import Singleton
from utils.units import RPM2RadPerSec, m2in
from wrappers.wrapperedSparkMax import WrapperedSparkMax


class GamePieceHandling(metaclass=Singleton):
    def __init__(self):
        # Booleans
        self.shooterOnCmd = False
        self.intakeOnCmd = False
        self.ejectOnCmd = False

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
        self._updateCals()

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

    def updateShooter(self, shouldRun):
        if(shouldRun):
            desVel = RPM2RadPerSec(self.shooterVel.get())
            self.shooterMotorLeft.setVelCmd(desVel,desVel*self.shooterkFCal.get())
            self.shooterMotorRight.setVelCmd(desVel,desVel*self.shooterkFCal.get())
        else:
            self.shooterMotorLeft.setVoltage(0.0)
            self.shooterMotorRight.setVoltage(0.0)


    def updateIntake(self, shouldRun):
        voltage = self.intakeVoltageCal.get() if shouldRun else 0.0
        self.intakeMotorUpper.setVoltage(voltage)
        self.intakeMotorLower.setVoltage(voltage)

    def updateFloorRoller(self, shouldRun):
        voltage = self.intakeVoltageCal.get() if shouldRun else 0.0
        self.floorRoolerMotor1.setVoltage(voltage)
        self.floorRoolerMotor2.setVoltage(voltage)

    def _updateCals(self):
            self.shooterMotorLeft.setPID(self.shooterkPCal.get(),0.0,0.0)
            self.shooterMotorRight.setPID(self.shooterkPCal.get(),0.0,0.0)

    def update(self):
        # Update PID Gains if needed
        if self.shooterkPCal.isChanged():
            self._updateCals()

        # TOF Sensor Update
        gamepieceDistSensorMeas = m2in(self.tofSensor.getRange() / 1000.0)
        self.disconTOFFault.set(self.tofSensor.getFirmwareVersion() == 0)

        if(self.disconTOFFault.isActive):
            # Gamepiece Sensor Faulted - assume we don't have a gamepiece
            self.hasGamePiece = False
        else:
            # Gampiece sensor ok - normal operation
            if gamepieceDistSensorMeas < self.gamePiecePresentCal.get():
                self.hasGamePiece = True
            elif gamepieceDistSensorMeas > self.gamePieceAbsentCal.get():
                self.hasGamePiece = False
            else:
                # Hystersis - hold state
                pass

        # Gamepiece Handling
        if self.intakeOnCmd:
            # Intake desired - run if we don't yet have a gamepiece
            if self.hasGamePiece:
                self.updateIntake(False)
                self.updateFloorRoller(False)
            else:
                self.updateIntake(True)
                self.updateFloorRoller(True)

            # And don't shoot
            self.updateShooter(False)
            
        elif self.shooterOnCmd:
            # Shooting Commanded
            self.updateShooter(True)
            self.updateFloorRoller(False)
            curShooterVel = max(abs(self.shooterMotorLeft.getMotorVelocityRadPerSec()),abs(self.shooterMotorRight.getMotorVelocityRadPerSec()))
            if abs(RPM2RadPerSec(self.shooterVel.get()) - curShooterVel) < RPM2RadPerSec(30.0):
                # We're at the right shooter speed, go ahead and inject the gamepiece
                self.updateIntake(True)
            else:
                # Wait for spoolup
                self.updateIntake(False)
        else:
            # Nothing commanded
            self.updateShooter(False)
            self.updateFloorRoller(False)
            self.updateIntake(False)

    # Take in command from the outside world
    def setInput(self, SingerShooterBoolean, SingerIntakeBoolean, SingerEjectBoolean):
        self.shooterOnCmd = SingerShooterBoolean
        self.intakeOnCmd = SingerIntakeBoolean
        self.ejectOnCmd = SingerEjectBoolean