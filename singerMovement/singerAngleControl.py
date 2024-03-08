from math import sin
from singerMovement.profiledAxis import ProfiledAxis
from singerMovement.singerConstants import (MAX_SINGER_ROT_ACCEL_DEGPS2, MAX_SINGER_ROT_VEL_DEG_PER_SEC, 
                                            SINGER_GEARBOX_RATIO, SINGER_ABS_ENC_OFF_DEG)
from utils.calibration import Calibration
from utils.constants import SINGER_ANGLE_MOTOR_CANID, SINGER_ANGLE_ABS_POS_ENC
from utils.units import deg2Rad, rad2Deg, sign
from utils.signalLogging import log
from rev import CANSparkMax
from rev import SparkAbsoluteEncoder

# Controls the singer angle motor, including rezeroing from absolute sensors
# and motion profiling
class SingerAngleControl():
    def __init__(self):
        # Singer Rotation Control
        self.motor = CANSparkMax(SINGER_ANGLE_MOTOR_CANID, CANSparkMax.MotorType.kBrushless)
        self.motor.setInverted(True)

        self.singerRotAbsSen = self.motor.getAbsoluteEncoder(SparkAbsoluteEncoder.Type.kDutyCycle)
        self.singerRotAbsSen.setPositionConversionFactor(6.283185)

        self.pidController = self.motor.getPIDController()

        # self.motor = WrapperedSparkMax(SINGER_ANGLE_MOTOR_CANID, "SingerRotMotor", brakeMode=False, currentLimitA=20.0)
        # self.motor.setInverted(True)
        # self.maxV = Calibration(name="Singer Max Rot Vel", default=MAX_SINGER_ROT_VEL_DEG_PER_SEC, units="degPerSec")
        # self.maxA = Calibration(name="Singer Max Rot Accel", default=MAX_SINGER_ROT_ACCEL_DEGPS2, units="degPerSec2")
        # self.profiler = ProfiledAxis()

        # self.kV = Calibration(name="Singer kV", default=0.045, units="V/rps")
        # self.kS = Calibration(name="Singer kS", default=0.4, units="V")
        # self.kG = Calibration(name="Singer kG", default=0.6, units="V/cos(deg)")
        self.kP = Calibration(name="Singer kP", default=0.15, units="V/RadErr")
        # self.kI = Calibration(name="Singer kI", default=0.0)
        # self.kD = Calibration(name="Singer kD", default=0.0)
        # self.kIz = Calibration(name="Singer kI zone", default=0.0)

        self.pidController.setFeedbackDevice(self.singerRotAbsSen)
        self.pidController.setP(self.kP.get())

        self.motorVelCmd = 0

        #Absolute position sensors
        # self.singerRotAbsSen = WrapperedThroughBoreHexEncoder(name="SingerRotAbsPosSen", port=SINGER_ANGLE_ABS_POS_ENC)

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
        # self.relEncOffsetRad = 0.0

        self.stopped = True
        # self.profiledPos = self.absEncOffsetDeg
        # self.curUnprofiledPosCmd = self.absEncOffsetDeg
        self.desPos = self.absEncOffsetDeg
        self.actPos = self.absEncOffsetDeg

        # self.motor.setPID(self.kP.get(), 0.0, 0.0)

    # Return the rotation of the signer as measured by the absolute sensor in radians
    def _getAbsRot(self):
        return self.singerRotAbsSen.getPosition() - deg2Rad(self.absEncOffsetDeg)

    def getAngleRad(self):
        return self._getAbsRot

    def atTarget(self) -> float:
        #return self.profiler.isFinished()
        return abs(self.desPos - rad2Deg(self.getAngleRad())) <= 6

    def setDesPos(self, desPos):
        self.stopped = False
        self.desPos = desPos

    def getDesPos(self):
        return self.desPos

    def setStopped(self):
        self.stopped = True
        self.curUnprofiledPosCmd = self.getAngleRad()
        #self.profiler.disable()
    
    def manualCtrl(self,cmdIn):
        self.motor.setVoltage(cmdIn)

    def update(self):
        actualPos = self.getAngleRad()
        
        # Update motor closed-loop calibration
        if(self.kP.isChanged()):
            self.pidController.setP(self.kP.get())

        if(self.stopped):
            self.motor.stopMotor()
            self.profiledPos = actualPos
        else:
            self.pidController.setReference(self.desPos, CANSparkMax.ControlType.kPosition)

        log("Singer Pos Des", rad2Deg(self.desPos),"deg")
        log("Singer Pos Act", rad2Deg(self.actPos) ,"deg")
        log("Singer at Target?", self.atTarget(), "bool")