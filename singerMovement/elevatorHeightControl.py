import math

from playingwithfusion import TimeOfFlight
from singerMovement.singerConstants import (ELEVATOR_GEARBOX_GEAR_RATIO, ELEVATOR_SPOOL_RADIUS_M, 
                                            MAX_CARRIAGE_ACCEL_MPS2, MAX_CARRIAGE_VEL_MPS)
from singerMovement.profiledAxis import ProfiledAxis
from utils.calibration import Calibration
from utils.units import sign
from utils.signalLogging import log
from wrappers.wrapperedSparkMax import WrapperedSparkMax

# Controls the elevator height motor, including rezeroing from absolute sensors
# and motion profiling
class ElevatorHeightControl():
    def __init__(self):
        # Elevator up/down control
        self.motor = WrapperedSparkMax(19, "ElevatorMotor", brakeMode=True,)
        self.maxV = Calibration(name="Elevator Max Vel", default=MAX_CARRIAGE_VEL_MPS, units="mps")
        self.maxA = Calibration(name="Elevator Max Accel", default=MAX_CARRIAGE_ACCEL_MPS2, units="mps2")
        self.profiler = ProfiledAxis()

        self.curUnprofiledPosCmd = 0

        self.heightAbsSen = TimeOfFlight(13)
        self.heightAbsSen.setRangingMode(TimeOfFlight.RangingMode.kShort, 24)
        self.heightAbsSen.setRangeOfInterest(6, 6, 10, 10)  # fov for sensor

        self.kV = Calibration(name="Elevator kV", default=0.0, units="V/rps")
        self.kS = Calibration(name="Elevator kS", default=0.0, units="V")

        self.stopped = True

        # Absolute Sensor mount offsets
        # After mounting the sensor, these should be tweaked one time
        # in order to adjust whatever the sensor reads into the reference frame
        # of the mechanism
        self.absOffsetM = 0.0

        # Relative Encoder Offsets
        # Releative encoders always start at 0 at power-on
        # However, we may or may not have the mechanism at the "zero" position when we powered on
        # These variables store an offset which is calculated from the absolute sensors
        # to make sure the relative sensors inside the encoders accurately reflect
        # the actual position of the mechanism
        self.relEncOffsetM = 0.0

        self.profiledPos = 0.0
        self.curUnprofiledPosCmd = 0.0


    def _motorRevToHeight(self, motorRev):
        return motorRev * 1/ELEVATOR_GEARBOX_GEAR_RATIO * (ELEVATOR_SPOOL_RADIUS_M * 2.0 * math.pi) - self.relEncOffsetM
            
    def _heightToMotorRev(self, elevLin):
        return ((elevLin + self.relEncOffsetM) * 1/(ELEVATOR_SPOOL_RADIUS_M * 2.0 * math.pi) 
                * ELEVATOR_GEARBOX_GEAR_RATIO )
    
    def getHeightM(self):
        motorRot = self.motor.getMotorPositionRad()
        elevPos = self._motorRevToHeight(motorRot)
        return elevPos
    
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
        return self.profiler.isFinished()
    
    def setDesPos(self, desPos):
        self.stopped = False
        self.curUnprofiledPosCmd = desPos
        self.profiler.set(desPos, self.maxV.get(), self.maxA.get(), self.getHeightM())

    def setStopped(self):
        self.stopped = True
        self.curUnprofiledPosCmd = self.getHeightM()
        self.profiler.disable()


    def getProfiledDesPos(self):
        return self.profiledPos

    def update(self):
        actualPos = self.getHeightM()

        if(self.stopped):
            self.motor.setVoltage(0.0)
            self.profiledPos = actualPos
        else:
            curState = self.profiler.getCurState()

            self.profiledPos = curState.position

            motorPosCmd = self._heightToMotorRev(curState.position)
            motorVelCmd = self._heightToMotorRev(curState.velocity)

            vFF = self.kV.get() * motorVelCmd  + self.kS.get() * sign(motorVelCmd)

            self.motor.setPosCmd(motorPosCmd, vFF)

        log("Elevator Pos Des", self.curUnprofiledPosCmd,"m")
        log("Elevator Pos Profiled", self.profiledPos ,"m")
        log("Elevator Pos Act", actualPos ,"m")