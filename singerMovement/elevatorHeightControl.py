
from playingwithfusion import TimeOfFlight
from rev import CANSparkMax, CANSparkLowLevel
from singerMovement.singerConstants import (ELEVATOR_GEARBOX_GEAR_RATIO, ELEVATOR_SPOOL_RADIUS_M, 
                                            MAX_CARRIAGE_ACCEL_MPS2, MAX_CARRIAGE_VEL_MPS)
from singerMovement.profiledAxis import ProfiledAxis
from utils.calibration import Calibration
from utils.units import sign
from utils.signalLogging import log
from utils.constants import ELEVATOR_HEIGHT_RIGHT_MOTOR_CANID, ELEVATOR_HEIGHT_LEFT_MOTOR_CANID, ELEVATOR_TOF_CANID
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from utils.singleton import Singleton

# Controls the elevator height motor, including rezeroing from absolute sensors
# and motion profiling
class ElevatorHeightControl(metaclass=Singleton):
    def __init__(self):
        # Elevator up/down control
        self.motor = WrapperedSparkMax(ELEVATOR_HEIGHT_RIGHT_MOTOR_CANID, "ElevatorMotor", brakeMode=True)
        self.motor.setInverted(True)
        self.otherMotor = CANSparkMax(ELEVATOR_HEIGHT_LEFT_MOTOR_CANID, CANSparkLowLevel.MotorType.kBrushless)
        self.otherMotor.setIdleMode(CANSparkMax.IdleMode.kBrake)
        self.otherMotor.follow(self.motor.ctrl, True)
        self.maxV = Calibration(name="Elevator Max Vel", default=MAX_CARRIAGE_VEL_MPS, units="mps")
        self.maxA = Calibration(name="Elevator Max Accel", default=MAX_CARRIAGE_ACCEL_MPS2, units="mps2")
        
        self.motorVelCmd = 0.0

        self.profiler = ProfiledAxis()

        self.heightAbsSen = TimeOfFlight(ELEVATOR_TOF_CANID)
        self.heightAbsSen.setRangingMode(TimeOfFlight.RangingMode.kShort, 24)
        self.heightAbsSen.setRangeOfInterest(6, 6, 10, 10)  # fov for sensor

        self.kV = Calibration(name="Elevator kV", default=0.02, units="V/rps")
        self.kS = Calibration(name="Elevator kS", default=0.1, units="V")
        self.kG = Calibration(name="Elevator kG", default=0.25, units="V")
        self.kP = Calibration(name="Elevator kP", default=0.05, units="V/rad error")

        self.motor.setPID(self.kV.get(), 0.0, 0.0)
        self.motor.setPID(self.kS.get(), 0.0, 0.0)
        self.motor.setPID(self.kG.get(), 0.0, 0.0)
        self.motor.setPID(self.kP.get(), 0.0, 0.0)

        self.stopped = True

        # Absolute Sensor mount offsets
        # After mounting the sensor, these should be tweaked one time
        # in order to adjust whatever the sensor reads into the reference frame
        # of the mechanism
        self.absOffsetM = 0.074

        # Relative Encoder Offsets
        # Releative encoders always start at 0 at power-on
        # However, we may or may not have the mechanism at the "zero" position when we powered on
        # These variables store an offset which is calculated from the absolute sensors
        # to make sure the relative sensors inside the encoders accurately reflect
        # the actual position of the mechanism
        self.relEncOffsetM = 0.0

        self.profiledPos = 0.0
        self.curUnprofiledPosCmd = 0.0


    def _motorRadToHeight(self, motorRad):
        return motorRad * 1/ELEVATOR_GEARBOX_GEAR_RATIO * (ELEVATOR_SPOOL_RADIUS_M) - self.relEncOffsetM

    def _heightToMotorRad(self, elevLin):
        return ((elevLin + self.relEncOffsetM) * 1/(ELEVATOR_SPOOL_RADIUS_M) 
                * ELEVATOR_GEARBOX_GEAR_RATIO )

    def _heightVeltoMotorVel(self, elevLinVel):
        return (elevLinVel * 1/(ELEVATOR_SPOOL_RADIUS_M) * ELEVATOR_GEARBOX_GEAR_RATIO )

    def getHeightM(self):
        return self._motorRadToHeight(self.motor.getMotorPositionRad())
    
    # Given the current profiler state, calculate the distance (in m) needed to stop
    # Uses displacement under constant acceleration equations
    # see https://www.ck12.org/book/ck-12-physics-concepts-intermediate/r3/section/2.6/ 
    # equation 3
    def getStoppingDistanceM(self):
        if(self.profiler.isFinished()):
            return 0.0
        else:
            state = self.profiler.getCurState()
            return state.velocity**2.0 / (2.0 * self.maxA.get()) * sign(state.velocity)

    
    # Return the height of the elevator as measured by the absolute sensor in meters
    def _getAbsHeight(self):
        return self.heightAbsSen.getRange() / 1000.0 - self.absOffsetM

    # This routine uses the absolute sensors to adjust the offsets for the relative sensors
    # so that the relative sensors match reality.
    # It should be called.... infrequently. Likely once shortly after robot init.
    def initFromAbsoluteSensor(self):
        # Reset offsets to zero, so the relative sensor get functions return
        # just whatever offset the relative sensor currently has.
        self.relEncOffsetM = 0.0

        # New Offset = real angle - current rel sensor offset ??
        self.relEncOffsetM = self._getAbsHeight() - self.getHeightM()
    
    def atTarget(self):
        return abs(self.curUnprofiledPosCmd - self.getHeightM()) <= .04

    def setDesPos(self, desPos):
        self.stopped = False
        self.curUnprofiledPosCmd = desPos
        self.profiler.set(desPos, self.maxV.get(), self.maxA.get(), self.getHeightM())

    def setStopped(self):
        #self.stopped = True
        self.curUnprofiledPosCmd = self.getHeightM()
        #self.profiler.disable()
    
    def getProfiledDesPos(self):
        return self.profiledPos

    def update(self):
        actualPos = self.getHeightM()

        # Update motor closed-loop calibration
        if(self.kP.isChanged()):
            self.motor.setPID(self.kP.get(), 0.0, 0.0)

        if(self.stopped):
            self.motor.setVoltage(0.0)
            self.profiledPos = actualPos
        else:
            curState = self.profiler.getCurState()

            self.profiledPos = curState.position

            motorPosCmd = self._heightToMotorRad(curState.position)
            self.motorVelCmd = self._heightVeltoMotorVel(curState.velocity)

            vFF = self.kV.get() * self.motorVelCmd  + self.kS.get() * sign(self.motorVelCmd) + self.kG.get()

            self.motor.setPosCmd(motorPosCmd, vFF)
            self.otherMotor.follow(self.motor.ctrl, True)

        log("Elevator Pos Des", self.curUnprofiledPosCmd,"m")
        log("Elevator Pos Profiled", self.profiledPos ,"m")
        log("Elevator Pos Act", actualPos ,"m")
        log("Elevator at Target?", self.atTarget(), "bool")