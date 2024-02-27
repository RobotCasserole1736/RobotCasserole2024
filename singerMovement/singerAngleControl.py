from math import sin
from singerMovement.singerConstants import (MAX_SINGER_ROT_ACCEL_DEGPS2, MAX_SINGER_ROT_VEL_DEG_PER_SEC, 
                                            SINGER_GEARBOX_RATIO, SINGER_ABS_ENC_OFF_DEG)
from singerMovement.profiledAxis import ProfiledAxis
from utils.calibration import Calibration
from utils.constants import SINGER_ANGLE_MOTOR_CANID, SINGER_ANGLE_ABS_POS_ENC
from utils.units import deg2Rad, rad2Deg, sign
from utils.signalLogging import log
from math import sin
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from wrappers.wrapperedThroughBoreHexEncoder import WrapperedThroughBoreHexEncoder

# Controls the singer angle motor, including rezeroing from absolute sensors
# and motion profiling
class SingerAngleControl():
    def __init__(self):
        # Singer Rotation Control
        self.motor = WrapperedSparkMax(SINGER_ANGLE_MOTOR_CANID, "SingerRotMotor", brakeMode=False, currentLimitA=20.0)
        self.maxV = Calibration(name="Singer Max Rot Vel", default=MAX_SINGER_ROT_VEL_DEG_PER_SEC, units="degPerSec")
        self.maxA = Calibration(name="Singer Max Rot Accel", default=MAX_SINGER_ROT_ACCEL_DEGPS2, units="degPerSec2")
        self.profiler = ProfiledAxis()

        self.kV = Calibration(name="Singer kV", default=0.02, units="V/rps")
        self.kS = Calibration(name="Singer kS", default=0.5, units="V")
        self.kG = Calibration(name="Singer kG", default=0.4, units="V/cos(deg)")
        self.kP = Calibration(name="Singer kP", default=0.4, units="V/RadErr")

        self.motorVelCmd = 0

        #Absolute position sensors
        self.singerRotAbsSen = WrapperedThroughBoreHexEncoder(name="SingerRotAbsPosSen", port=SINGER_ANGLE_ABS_POS_ENC)

        # Absolute Sensor mount offsets
        # After mounting the sensor, these should be tweaked one time
        # in order to adjust whatever the sensor reads into the reference frame
        # of the mechanism
        self.absEncOffsetDeg = SINGER_ABS_ENC_OFF_DEG

        # Relative Encoder Offsets
        # Releative encoders always start at 0 at power-on
        # However, we may or may not have the mechanism at the "zero" position when we powered on
        # These variables store an offset which is calculated from the absolute sensors
        # to make sure the relative sensors inside the encoders accurately reflect
        # the actual position of the mechanism
        self.relEncOffsetRad = 0.0

        self.stopped = True
        self.profiledPos = self.absEncOffsetDeg
        self.curUnprofiledPosCmd = self.absEncOffsetDeg

        self.motor.setPID(self.kP.get(), 0.0, 0.0)

    # Return the rotation of the signer as measured by the absolute sensor in radians
    def _getAbsRot(self):
        return self.singerRotAbsSen.getAngleRad() - deg2Rad(self.absEncOffsetDeg)

    # This routine uses the absolute sensors to adjust the offsets for the relative sensors
    # so that the relative sensors match reality.
    # It should be called.... infrequently. Likely once shortly after robot init.
    def initFromAbsoluteSensor(self):
        # Reset relative offset to zero, so the relative sensor get functions return
        # just whatever offset the relative sensor currently has.
        self.relEncOffsetRad = 0.0

        # New Offset = real angle - current rel sensor offset ??
        self.relEncOffsetRad = self._getAbsRot() - self.getAngleRad()

    def _motorRadToAngleRad(self, motorRev):
        return motorRev * 1/SINGER_GEARBOX_RATIO - self.relEncOffsetRad
            
    def _angleRadToMotorRad(self, singerAngleRad):
        return (singerAngleRad + self.relEncOffsetRad) * SINGER_GEARBOX_RATIO
    
    def _angleVelToMotorVel(self, singerAngleVel):
        return singerAngleVel * SINGER_GEARBOX_RATIO
    
    def getAngleRad(self):
        motorRot = self.motor.getMotorPositionRad()
        singerAngle = self._motorRadToAngleRad(motorRot)
        return singerAngle
    
    # Given the current profiler state, calculate the distance (in radians) needed to stop
    # Uses displacement under constant acceleration equations
    # see https://www.ck12.org/book/ck-12-physics-concepts-intermediate/r3/section/2.6/ 
    # equation 3
    def getStoppingDistanceRad(self):
        if(self.profiler.isFinished()):
            return 0.0
        else:
            state = self.profiler.getCurState()
            return state.velocity**2.0 / (2.0 * deg2Rad(self.maxA.get())) * sign(state.velocity)

    
    
    def atTarget(self):
        #return self.profiler.isFinished()
        return abs(rad2Deg(self.curUnprofiledPosCmd - self.getAngleRad())) <= 6

    def setDesPos(self, desPos):
        self.stopped = False
        self.curUnprofiledPosCmd = desPos
        self._setProfile(self.curUnprofiledPosCmd)

    def setStopped(self):
        #self.stopped = True
        self.curUnprofiledPosCmd = self.getAngleRad()
        #self.profiler.disable()

    def _setProfile(self, desPos):
        self.profiler.set(desPos, deg2Rad(self.maxV.get()), deg2Rad(self.maxA.get()), self.getAngleRad())

    def getProfiledDesPos(self):
        return self.profiledPos
    
    def manualCtrl(self,cmdIn):
        self.motor.setVoltage(cmdIn)

    def update(self):
        actualPos = self.getAngleRad()

        # Update motor closed-loop calibration
        if(self.kP.isChanged()):
            self.motor.setPID(self.kP.get(), 0.0, 0.0)

        if(self.stopped):
            self.motor.setVoltage(0.0)
            self.profiledPos = actualPos
        else:
            curState = self.profiler.getCurState()

            self.profiledPos = curState.position

            motorPosCmd = self._angleRadToMotorRad(curState.position)
            self.motorVelCmd = self._angleVelToMotorVel(curState.velocity)

            vFF = self.kV.get() * self.motorVelCmd + self.kS.get() * sign(self.motorVelCmd) - self.kG.get() * sin(actualPos)

            self.motor.setPosCmd(motorPosCmd, vFF)


        log("Singer Pos Des", rad2Deg(self.curUnprofiledPosCmd),"deg")
        log("Singer Pos Profiled", rad2Deg(self.profiledPos) ,"deg")
        log("Singer Pos Act", rad2Deg(actualPos) ,"deg")
        log("Singer Motor Vel Cmd", self.motorVelCmd)
        log("Singer at Target?", self.atTarget(), "bool")