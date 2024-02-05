#this will be in distance along the elevator, with 0 being at bottom and the top being whatever it is
from wpilib import Timer
from enum import Enum
import math
from singerMovement.singerConstants import ELEVATOR_GEARBOX_GEAR_RATIO, MAX_CARRIAGE_ACCEL_MPS2, MAX_CARRIAGE_VEL_MPS, MAX_SINGER_ROT_ACCEL_DEGPS2, MAX_SINGER_ROT_VEL_DEG_PER_SEC, ELEVATOR_SPOOL_RADIUS_M, SINGER_GEARBOX_RATIO
from utils.singleton import Singleton
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from utils.calibration import Calibration
from utils.units import deg2Rad
from wpimath.trajectory import TrapezoidProfile
from playingwithfusion import TimeOfFlight
from wrappers.wrapperedThroughBoreHexEncoder import WrapperedThroughBoreHexEncoder

class _CarriageStateMachine(Enum):
    HOLD_ALL = 0
    RUN_TO_SAFE_HEIGHT = 1
    ROT_AT_SAFE_HEIGHT = 2
    DESCEND_BELOW_SAFE_HEIGHT = 3
    RUN_TO_HEIGHT = 4
    ROTATE_TO_ANGLE = 5

class CarriageControlCmd(Enum):
    HOLD = 0
    INTAKE = 1
    AUTO_ALIGN = 2
    AMP = 3
    TRAP = 4

class CarriageControl(metaclass=Singleton):

    def __init__(self):
        # Carriage up/down control
        self.upDownSingerMotor = WrapperedSparkMax(1, "carriageUpDownMotor", False)
        self.kMaxVUpDown = Calibration(name="Carriage Max Vel", default=MAX_CARRIAGE_VEL_MPS, units="mps")
        self.kMaxAUpDown = Calibration(name="Carriage Max Accel", default=MAX_CARRIAGE_ACCEL_MPS2, units="mps2")

        # Singer Rotation Control
        self.rotSingerMotor = WrapperedSparkMax(2, "carriageRotMotor", False)
        self.kMaxVRot = Calibration(name="Singer Max Rot Vel", default=MAX_SINGER_ROT_VEL_DEG_PER_SEC, units="degPerSec")
        self.kMaxARot = Calibration(name="Singer Max Rot Accel", default=MAX_SINGER_ROT_ACCEL_DEGPS2, units="degPerSec2")

        # Fixed Position Cal's
        self.singerRotIntake = Calibration(name="Singer Rot Intake", units="deg", default=60.0 )
        self.singerRotAmp= Calibration(name="Singer Rot Amp", units="deg", default=-20.0 )
        self.singerRotTrap = Calibration(name="Singer Rot Trap", units="deg", default=-20.0 )

        self.elevatorHeightIntake = Calibration(name="Elev Height Intake", units="m", default=0.0 )
        self.elevatorHeightAmp= Calibration(name="Elev Height Amp", units="m", default=0.75 )
        self.elevatorHeightTrap = Calibration(name="Elev Height Trap", units="m", default=0.75 )
        self.elevatorHeightAutoAlign = Calibration(name="Elev Height AutoAlign", units="m", default=0.5 )

        # Minimum height that we have to go to before we can freely rotate the singer
        self.elevatorMinSafeHeight = Calibration(name="Elev Min Safe Height", units="m", default=0.65 )


        # Absolute Sensor mount offsets
        # After mounting the sensor, these should be tweaked one time
        # in order to adjust whatever the sensor reads into the reference frame
        # of the mechanism
        self.singerRotAbsEncOffsetDeg = 0.0
        self.elevatorHeightAbsOffsetM = 0.0

        # Relative Encoder Offsets
        # Releative encoders always start at 0 at power-on
        # However, we may or may not have the mechanism at the "zero" position when we powered on
        # These variables store an offset which is calculated from the absolute sensors
        # to make sure the relative sensors inside the encoders accurately reflect
        # the actual position of the mechanism
        self.singerRotRelEncOffsetRad = 0.0
        self.elevatorHeightRelEncOffsetM = 0.0

        #Absolute position sensors
        self.singerRotAbsSen = WrapperedThroughBoreHexEncoder(name="SingerRotAbsPosSen", port=2)
        self.elevatorHeightAbsSen = TimeOfFlight(13)
        self.elevatorHeightAbsSen.setRangingMode(TimeOfFlight.RangingMode.kShort, 24)
        self.elevatorHeightAbsSen.setRangeOfInterest(6, 6, 10, 10)  # fov for sensor

        self.elevatorProfileConstraints = TrapezoidProfile.Constraints(maxVelocity=self.kMaxVUpDown.get(), maxAcceleration=self.kMaxAUpDown.get())
        self.singerRotateConstraints = TrapezoidProfile.Constraints(maxVelocity=self.kMaxVRot.get(), maxAcceleration=self.kMaxARot.get())

        self.curElevHeight = 0.0
        self.curSingerRot = 0.0
        self.desElevHeight = 0.0
        self.desSingerRot = 0.0
        self.profiledElevHeight = 0.0
        self.profiledSingerRot = 0.0

        self.curPosCmd = CarriageControlCmd.HOLD
        self.prevPosCmd = CarriageControlCmd.HOLD

    # Use the current position command to calculate
    # The unprofiled elevator height in meters
    def _getUnprofiledElevHeightCmd(self):
        if(self.curPosCmd == CarriageControlCmd.HOLD):
            return self.curElevHeight
        elif(self.curPosCmd == CarriageControlCmd.INTAKE):
            return self.elevatorHeightIntake.get()
        elif(self.curPosCmd == CarriageControlCmd.AMP):
            return self.elevatorHeightAmp.get()
        elif(self.curPosCmd == CarriageControlCmd.TRAP):
            return self.elevatorHeightTrap.get()
        elif(self.curPosCmd == CarriageControlCmd.AUTO_ALIGN):
            return self.elevatorHeightAutoAlign.get()

    # Use the current position command to calculate
    # The unprofiled elevator height in radians
    def _getUnprofiledSingerRotCmd(self):
        if(self.curPosCmd == CarriageControlCmd.HOLD):
            return self.curSingerRot
        elif(self.curPosCmd == CarriageControlCmd.INTAKE):
            return deg2Rad(self.singerRotIntake.get())
        elif(self.curPosCmd == CarriageControlCmd.AMP):
            return deg2Rad(self.singerRotAmp.get())
        elif(self.curPosCmd == CarriageControlCmd.TRAP):
            return deg2Rad(self.singerRotTrap.get())
        elif(self.curPosCmd == CarriageControlCmd.AUTO_ALIGN):
            return self.autoAlignSingerRotCmd 

    # Return the rotation of the signer as measured by the absolute sensor in radians
    def _getSingerAbsRot(self):
        return self.singerRotAbsSen.getAngleRad() - deg2Rad(self.singerRotAbsEncOffsetDeg)

    # Return the height of the elevator as measured by the absolute sensor in meters
    def _getElevatorAbsHeight(self):
        return self.elevatorHeightAbsSen.getRange() / 1000.0 - self.elevatorHeightAbsOffsetM

    # This routine uses the absolute sensors to adjust the offsets for the relative sensors
    # so that the relative sensors match reality.
    # It should be called.... infrequently. Likely once shortly after robot init.
    def initFromAbsoluteSensors(self):
        # Reset offsets to zero, so the relative sensor get functions return
        # just whatever offset the relative sensor currently has.
        self.singerRotRelEncOffsetRad = 0.0
        self.elevatorHeightRelEncOffsetM = 0.0

        # New Offset = real angle - current rel sensor offset ??
        self.singerRotRelEncOffsetRad = self._getSingerAbsRot() - self.getSingerAngle()
        self.elevatorHeightRelEncOffsetM = self._getElevatorAbsHeight() - self.getElevatorHeightM()

    def _motorRevToElevatorLinearDisp(self, motorRev):
        return motorRev * 1/ELEVATOR_GEARBOX_GEAR_RATIO * (ELEVATOR_SPOOL_RADIUS_M * 2.0 * math.pi)
            
    def _elevatorLinearDispToMotorRev(self, elevLin):
        return elevLin * 1/(ELEVATOR_SPOOL_RADIUS_M * 2.0 * math.pi) * ELEVATOR_GEARBOX_GEAR_RATIO
    
    def getElevatorHeightM(self):
        motorRot = self.upDownSingerMotor.getMotorPositionRad()
        elevPos = self._motorRevToElevatorLinearDisp(motorRot) - self.elevatorHeightRelEncOffsetM
        return elevPos
    
    def _motorRevToSingerAngle(self, motorRev):
        return motorRev * 1/SINGER_GEARBOX_RATIO 
            
    def _singerAngleToMotorRev(self, elevLin):
        return elevLin * SINGER_GEARBOX_RATIO
    
    def getSingerAngle(self):
        motorRot = self.upDownSingerMotor.getMotorPositionRad()
        elevPos = self._motorRevToElevatorLinearDisp(motorRot) - self.elevatorHeightRelEncOffsetM
        return elevPos

    def _remakeProfiles(self):
        #new setpoint, need to recalculate trajectory
        self.profileStartTime = Timer.getFPGATimestamp()
        self.singerRotProfile = TrapezoidProfile(self.elevatorProfileConstraints,curSetpoint,self.prevProfiledSetpoint)
        self.singerRotProfile = TrapezoidProfile(self.elevatorProfileConstraints,curSetpoint,self.prevProfiledSetpoint)
        

    def update(self):
 
        #up/down
        #curSetpoint = can't be drivetrain setpoint because it's carriage?
        curTime = Timer.getFPGATimestamp()

        if(self.prevPosCmd != self.curPosCmd):
            self._remakeProfiles()

        curCmdState = profile.calculate(curTime - self.profileStartTime)
        # Use curCmdState.velocity and .position for feedforward and feedback motor control

        self.prevCmdState = curCmdState







    #will need to get command position from the operator controller and
    #desired singer angle for autolign"""

    def setSignerAutoAlignAngle(self, desiredAngle:float):
        self.autoAlignSingerRotCmd = desiredAngle
    
    def setPositionCmd(self, curPosCmdIn: CarriageControlCmd):
        self.curPosCmd = curPosCmdIn