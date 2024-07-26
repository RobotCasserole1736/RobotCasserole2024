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
from utils.units import RPM2RadPerSec, m2in, radPerSec2RPM
from utils.signalLogging import log
from wrappers.wrapperedSparkMax import WrapperedSparkMax



class GamePieceHandling(metaclass=Singleton):
    
    
    
    def __init__(self):

        # Booleans
        self.spoolUpCmd = False
        self.shooterSpooledUp = False
        self.shooterOnCmd = False
        self.intakeOnCmd = False
        self.ejectOnCmd = False
        self.intakeRunning = False

        # Shooter Motors
        self.shooterMotorLeft = WrapperedSparkMax(
            constants.SHOOTER_MOTOR_LEFT_CANID, "ShooterMotorLeft"
        )
        self.shooterMotorLeft.setInverted(True)
        self.shooterMotorRight = WrapperedSparkMax(
            constants.SHOOTER_MOTOR_RIGHT_CANID, "ShooterMotorRight"
        )
        self.curShooterVel = 0

        # Intake Motors
        self.intakeMotorUpper = WrapperedSparkMax(constants.INTAKE_MOTOR_UPPER_CANID, "IntakeMotorUpper")
        self.intakeMotorLower = WrapperedSparkMax(constants.INTAKE_MOTOR_LOWER_CANID, "IntakeMotorLower")

        # Floor Roller Motors
        self.floorRoolerMotor1 = WrapperedSparkMax(
            constants.FLOORROLLER_MOTOR1_CANID, "FloorRollerMotor1"
        )

        self.tofFault = faults.Fault("Claw TOF Sensor is Disconnected")

        # Shooter Calibrations (PID Controller)
        self.shooterkFCal = Calibration("ShooterRightkF", 0.0024, "V/RPM")
        self.shooterkPCal = Calibration("ShooterkP", 0.0002)
        self.shooterVel = Calibration("Shooter Speaker Velocity", 4700, "RPM")
        self.shooterAmpVel = Calibration("Shooter Amp Velocity", 1736, "RPM")
        self._updateCals()

        # Intake Voltage Calibration
        self.intakeVoltageCal = Calibration("IntakeVoltage", 12, "V")
        self.sushiRollerVoltageCal = Calibration("SushiRollervoltage", 12, "V")
        self.feedBackSlowCal = Calibration("FeedBackSlowVoltage", 1.5, "V")

        # Time of Flight sensor
        self.tofSensor = TimeOfFlight(constants.GAMEPIECE_HANDLING_TOF_CANID)
        self.tofSensor.setRangingMode(TimeOfFlight.RangingMode.kShort, 24)
        self.tofSensor.setRangeOfInterest(6, 6, 10, 10)  # fov for sensor

        # Calibrations for Gamepiece being absent and present
        self.gamePiecePresentCal = Calibration("NotePresentThresh", 10, "in")
        self.gamePieceAbsentCal = Calibration("NoteAbsentThresh", 12, "in")
        self.gamePieceInPlaceLowCal = Calibration("NoteInPlaceLow", 3, "in")
        self.gamePieceInPlaceHighCal = Calibration("NoteInPlaceHigh", 7, "in")

        self.hasGamePiece = False
        self.noteInPlace = False
        self.isAmpShot = False

        # TOF Disconnected Fault
        self.disconTOFFault = faults.Fault("Singer TOF Sensor is Disconnected")

    def updateShooter(self, shouldRun):
        if (shouldRun) and not self.isAmpShot:
            desVel = RPM2RadPerSec(self.shooterVel.get())
            self.shooterMotorLeft.setVelCmd(desVel,self.shooterVel.get()*self.shooterkFCal.get())
            self.shooterMotorRight.setVelCmd(desVel,self.shooterVel.get()*self.shooterkFCal.get())
            
        elif(shouldRun) and self.isAmpShot:
            desVel = RPM2RadPerSec(self.shooterAmpVel.get())
            self.shooterMotorLeft.setVelCmd(desVel,self.shooterAmpVel.get()*self.shooterkFCal.get())
            self.shooterMotorRight.setVelCmd(desVel,self.shooterAmpVel.get()*self.shooterkFCal.get())
        
        else:
            self.shooterMotorLeft.setVoltage(0.0)
            self.shooterMotorRight.setVoltage(0.0)
            

    def feedBackSlow(self, shouldRun):
        voltage = self.feedBackSlowCal.get() if shouldRun else 0.0
        self.intakeMotorLower.setVoltage(-voltage)
        self.intakeMotorUpper.setVoltage(-voltage)

    def updateIntake(self, shouldRun):
        voltage = self.intakeVoltageCal.get() if shouldRun else 0.0
        self.intakeMotorUpper.setVoltage(voltage)
        self.intakeMotorLower.setVoltage(voltage)
    
    def updateEject(self, shouldRun):
        voltage = self.intakeVoltageCal.get() if shouldRun else 0.0
        self.intakeMotorUpper.setVoltage(-voltage)
        self.intakeMotorLower.setVoltage(-voltage)
        self.floorRoolerMotor1.setVoltage(voltage)

    def updateFloorRoller(self, shouldRun):
        voltage = self.sushiRollerVoltageCal.get() if shouldRun else 0.0
        self.floorRoolerMotor1.setVoltage(-voltage)

    def _updateCals(self):
        self.shooterMotorLeft.setPID(self.shooterkPCal.get(),0.0,0.0)
        self.shooterMotorRight.setPID(self.shooterkPCal.get(),0.0,0.0)

    def setIsAmpShot(self, isAmpShot):
        self.isAmpShot = isAmpShot

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
                if gamepieceDistSensorMeas > self.gamePieceInPlaceLowCal.get() and \
                    gamepieceDistSensorMeas < self.gamePieceInPlaceHighCal.get():
                    self.feedBackSlow(False)
                    self.noteInPlace = True
                else:
                    self.feedBackSlow(True)
                    self.noteInPlace = False
            else:
                self.updateIntake(True)
                self.updateFloorRoller(True)

            # And don't shoot
            self.updateShooter(False)

        elif self.spoolUpCmd:
            # Shooting Commanded
            self.updateShooter(True)
            self.updateFloorRoller(False)
            self.feedBackSlow(False)
            self.curShooterVel = (max(abs(self.shooterMotorLeft.getMotorVelocityRadPerSec()),
                                abs(self.shooterMotorRight.getMotorVelocityRadPerSec())))
            # We're at the right shooter speed, go ahead and inject the gamepiece
            self.shooterSpooledUp = abs(RPM2RadPerSec(self.shooterVel.get()) - self.curShooterVel)\
                  < RPM2RadPerSec(250.0)
            if self.shooterSpooledUp and self.shooterOnCmd:
                self.updateIntake(True)
            else:
                self.updateIntake(False)

        elif self.ejectOnCmd:
            self.updateEject(True)

        else:
            # Nothing commanded
            self.updateShooter(False)
            self.updateFloorRoller(False)
            self.updateIntake(False)
            self.updateEject(False)

        log("Has Game Piece", self.hasGamePiece)
        log("TOF Distance",gamepieceDistSensorMeas)
        log("Cur Shooter Velocity", radPerSec2RPM(self.curShooterVel) , "RPM")

    # Take in command from the outside world
    def setInput(self, singerSpoolUpBoolean, singerIntakeBoolean, singerEjectBoolean, singerShootBoolean):
        self.spoolUpCmd = singerSpoolUpBoolean
        self.intakeOnCmd = singerIntakeBoolean
        self.ejectOnCmd = singerEjectBoolean
        self.shooterOnCmd = singerShootBoolean
        
    def getShooterMotorSpeed(self):
        return min(abs(radPerSec2RPM(self.shooterMotorLeft.getMotorVelocityRadPerSec())), \
        abs(radPerSec2RPM(self.shooterMotorRight.getMotorVelocityRadPerSec())))
    
    def getHasGamePiece(self):
        return self.hasGamePiece

    def getNoteInPlace(self):
        return self.noteInPlace
