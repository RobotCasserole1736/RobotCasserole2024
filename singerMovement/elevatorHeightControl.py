
from playingwithfusion import TimeOfFlight
from singerMovement.singerConstants import (ELEVATOR_GEARBOX_GEAR_RATIO, ELEVATOR_SPOOL_RADIUS_M, 
                                            MAX_CARRIAGE_ACCEL_MPS2, MAX_CARRIAGE_VEL_MPS)
from singerMovement.profiledAxis import ProfiledAxis
from utils.calibration import Calibration
from utils.units import sign
from utils.signalLogging import log
from utils.constants import ELEVATOR_HEIGHT_RIGHT_MOTOR_CANID, ELEVATOR_HEIGHT_LEFT_MOTOR_CANID, ELEVATOR_TOF_CANID
from wrappers.wrapperedSparkMax import WrapperedSparkMax

# Controls the elevator height motor, including rezeroing from absolute sensors
# and motion profiling
class ElevatorHeightControl():
    def __init__(self):
        # Elevator up/down control
        self.motorRight = WrapperedSparkMax(ELEVATOR_HEIGHT_RIGHT_MOTOR_CANID, "ElevatorMotorRight", brakeMode=False)
        self.motorLeft = WrapperedSparkMax(ELEVATOR_HEIGHT_LEFT_MOTOR_CANID, "ElevatorMotorLeft", brakeMode=False)

        # Right motor needs to be inverted so that positive vel/pos is going up
        self.motorRight.setInverted(True)
        self.maxV = Calibration(name="Elevator Max Vel", default=MAX_CARRIAGE_VEL_MPS, units="mps")
        self.maxA = Calibration(name="Elevator Max Accel", default=MAX_CARRIAGE_ACCEL_MPS2, units="mps2")
        self.profiler = ProfiledAxis()

        self.curUnprofiledPosCmd = 0

        self.motorVelCmd = 0

        self.heightAbsSen = TimeOfFlight(ELEVATOR_TOF_CANID)
        self.heightAbsSen.setRangingMode(TimeOfFlight.RangingMode.kShort, 24)
        self.heightAbsSen.setRangeOfInterest(6, 6, 10, 10)  # fov for sensor

        self.kV = Calibration(name="Elevator kV", default=0.0, units="V/rps")
        self.kS = Calibration(name="Elevator kS", default=0.0, units="V")
        self.kG = Calibration(name="Elevator kG", default=0.0, units="V")
        self.kP = Calibration(name="Elevator kP", default=0.0, units="V/rad error")

        self.motorRight.setPID(self.kV.get(), 0.0, 0.0)
        self.motorRight.setPID(self.kS.get(), 0.0, 0.0)
        self.motorRight.setPID(self.kG.get(), 0.0, 0.0)
        self.motorRight.setPID(self.kP.get(), 0.0, 0.0)

        self.stopped = True

        # Absolute Sensor mount offsets
        # After mounting the sensor, these should be tweaked one time
        # in order to adjust whatever the sensor reads into the reference frame
        # of the mechanism
        self.absOffsetM = 0.256

        # Relative Encoder Offsets
        # Releative encoders always start at 0 at power-on
        # However, we may or may not have the mechanism at the "zero" position when we powered on
        # These variables store an offset which is calculated from the absolute sensors
        # to make sure the relative sensors inside the encoders accurately reflect
        # the actual position of the mechanism
        self.relEncRightOffsetM = 0.0
        self.relEncLeftOffsetM = 0.0

        self.profiledPos = 0.0
        self.curUnprofiledPosCmd = 0.0


    def _motorRadToHeight(self, motorRad, relOffsetM):
        return motorRad * 1/ELEVATOR_GEARBOX_GEAR_RATIO * (ELEVATOR_SPOOL_RADIUS_M) - relOffsetM

    def _heightToMotorRad(self, elevLin, relOffsetM):
        return ((elevLin + relOffsetM) * 1/(ELEVATOR_SPOOL_RADIUS_M) 
                * ELEVATOR_GEARBOX_GEAR_RATIO )

    def _heightVeltoMotorVel(self, elevLinVel):
        return (elevLinVel * 1/(ELEVATOR_SPOOL_RADIUS_M) * ELEVATOR_GEARBOX_GEAR_RATIO )

    def getHeightM(self):
        return max(self._motorRadToHeight(self.motorRight.getMotorPositionRad(), self.relEncRightOffsetM),
                   self._motorRadToHeight(self.motorRight.getMotorPositionRad(), self.relEncLeftOffsetM))

    # Return the height of the elevator as measured by the absolute sensor in meters
    def _getAbsHeight(self):
        return self.heightAbsSen.getRange() / 1000.0 - self.absOffsetM

    # This routine uses the absolute sensors to adjust the offsets for the relative sensors
    # so that the relative sensors match reality.
    # It should be called.... infrequently. Likely once shortly after robot init.
    def initFromAbsoluteSensor(self):
        # Reset offsets to zero, so the relative sensor get functions return
        # just whatever offset the relative sensor currently has.
        self.relEncRightOffsetM = 0.0
        self.relEncLeftOffsetM = 0.0

        # New Offset = real angle - current rel sensor offset ??
        self.relEncRightOffsetM = self._getAbsHeight() - self.getHeightM()
        self.relEncLeftOffsetM = self._getAbsHeight() - self.getHeightM()

    def atTarget(self):
        return self.profiler.isFinished()
    
    def setDesPos(self, desPos):
        self.stopped = False
        self.curUnprofiledPosCmd = desPos
        self.profiler.set(desPos, self.maxV.get(), self.maxA.get(), self.getHeightM())

    def setStopped(self, relOffsetM):
        self.stopped = True
        self.curUnprofiledPosCmd = self.getHeightM()
        self.profiler.disable()
    
    def getProfiledDesPos(self):
        return self.profiledPos

    def update(self):
        actualPos = self.getHeightM()

        # Update motor closed-loop calibration
        if(self.kP.isChanged()):
            self.motorRight.setPID(self.kP.get(), 0.0, 0.0)
            self.motorLeft.setPID(self.kP.get(), 0.0, 0.0)

        if(self.stopped):
            self.motorLeft.setVoltage(0.0)
            self.motorRight.setVoltage(0.0)
            self.profiledPos = actualPos
        else:
            curState = self.profiler.getCurState()

            self.profiledPos = curState.position

            motorRightPosCmd = self._heightToMotorRad(curState.position, self.relEncRightOffsetM)
            motorLeftPosCmd = self._heightToMotorRad(curState.position, self.relEncLeftOffsetM)
            self.motorVelCmd = self._heightVeltoMotorVel(curState.velocity)

            vFF = self.kV.get() * self.motorVelCmd + self.kS.get() * sign(self.motorVelCmd) + self.kG.get()

            self.motorRight.setPosCmd(motorRightPosCmd, vFF)
            self.motorRight.setPosCmd(motorLeftPosCmd, vFF)

        log("Elevator Pos Des", self.curUnprofiledPosCmd,"m")
        log("Elevator Pos Profiled", self.profiledPos ,"m")
        log("Elevator Pos Act", actualPos ,"m")
        log("Elevator Height", self.heightAbsSen.getRange(),"m")
        log("Elevator Vel Cmd", self.motorVelCmd)
        log("Elevator Rmotor Rad Pos", self.motorRight.getMotorPositionRad())
        log("Elevator Lmotor Rad Pos", self.motorLeft.getMotorPositionRad())