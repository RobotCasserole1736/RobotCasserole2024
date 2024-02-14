from singerMovement.singerConstants import (MAX_SINGER_ROT_ACCEL_DEGPS2, MAX_SINGER_ROT_VEL_DEG_PER_SEC, 
                                            SINGER_GEARBOX_RATIO)
from singerMovement.profiledAxis import ProfiledAxis
from utils.calibration import Calibration
from utils.units import deg2Rad, rad2Deg, sign
from utils.signalLogging import log
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from wrappers.wrapperedThroughBoreHexEncoder import WrapperedThroughBoreHexEncoder

# Controls the singer angle motor, including rezeroing from absolute sensors
# and motion profiling
class SingerAngleControl():
    def __init__(self):
        # Singer Rotation Control
        self.motor = WrapperedSparkMax(SINGER_ANGLE_CANID, "SingerRotMotor", brakeMode=True, currentLimitA=20.0)
        self.maxV = Calibration(name="Singer Max Rot Vel", default=MAX_SINGER_ROT_VEL_DEG_PER_SEC, units="degPerSec")
        self.maxA = Calibration(name="Singer Max Rot Accel", default=MAX_SINGER_ROT_ACCEL_DEGPS2, units="degPerSec2")
        self.profiler = ProfiledAxis()

        self.kV = Calibration(name="Singer kV", default=0.0, units="V/rps")
        self.kS = Calibration(name="Singer kS", default=0.0, units="V")


        #Absolute position sensors
        self.singerRotAbsSen = WrapperedThroughBoreHexEncoder(name="SingerRotAbsPosSen", port=4)

        # Absolute Sensor mount offsets
        # After mounting the sensor, these should be tweaked one time
        # in order to adjust whatever the sensor reads into the reference frame
        # of the mechanism
        self.absEncOffsetDeg = 0.0

        # Relative Encoder Offsets
        # Releative encoders always start at 0 at power-on
        # However, we may or may not have the mechanism at the "zero" position when we powered on
        # These variables store an offset which is calculated from the absolute sensors
        # to make sure the relative sensors inside the encoders accurately reflect
        # the actual position of the mechanism
        self.relEncOffsetRad = 0.0

        self.stopped = True
        self.profiledPos = 0.0
        self.curUnprofiledPosCmd = 0.0

    # Return the rotation of the signer as measured by the absolute sensor in radians
    def _getAbsRot(self):
        return self.singerRotAbsSen.getAngleRad() - deg2Rad(self.absEncOffsetDeg)

    # This routine uses the absolute sensors to adjust the offsets for the relative sensors
    # so that the relative sensors match reality.
    # It should be called.... infrequently. Likely once shortly after robot init.
    def initFromAbsoluteSensor(self):
        # Reset offsets to zero, so the relative sensor get functions return
        # just whatever offset the relative sensor currently has.
        self.relEncOffsetRad = 0.0

        # New Offset = real angle - current rel sensor offset ??
        self.relEncOffsetRad = self._getAbsRot() - self.getAngle()

    def _motorRevToAngle(self, motorRev):
        return motorRev * 1/SINGER_GEARBOX_RATIO - self.relEncOffsetRad
            
    def _angleToMotorRev(self, elevLin):
        return (elevLin + self.relEncOffsetRad) * SINGER_GEARBOX_RATIO
    
    def getAngle(self):
        motorRot = self.motor.getMotorPositionRad()
        singerAngle = self._motorRevToAngle(motorRot)
        return singerAngle
    
    def atTarget(self):
        return self.profiler.isFinished()

    def setDesPos(self, desPos):
        self.stopped = False
        self.curUnprofiledPosCmd = desPos
        self._setProfile(self.curUnprofiledPosCmd)

    def setStopped(self):
        self.stopped = True
        self.curUnprofiledPosCmd = self.getAngle()
        self.profiler.disable()

    def _setProfile(self, desPos):
        self.profiler.set(desPos, deg2Rad(self.maxV.get()), deg2Rad(self.maxA.get()), self.getAngle())

    def getProfiledDesPos(self):
        return self.profiledPos

    def update(self):
        actualPos = self.getAngle()
        
        if(self.stopped):
            self.motor.setVoltage(0.0)
            self.profiledPos = actualPos
        else:
            curState = self.profiler.getCurState()

            self.profiledPos = curState.position

            motorPosCmd = self._angleToMotorRev(curState.position)
            motorVelCmd = self._angleToMotorRev(curState.velocity)

            vFF = self.kV.get() * motorVelCmd  + self.kS.get() * sign(motorVelCmd)

            self.motor.setPosCmd(motorPosCmd, vFF)

        log("Singer Pos Des", rad2Deg(self.curUnprofiledPosCmd),"deg")
        log("Singer Pos Profiled", rad2Deg(self.profiledPos) ,"deg")
        log("Singer Pos Act", rad2Deg(actualPos) ,"deg")