from math import sin
from singerMovement.profiledAxis import ProfiledAxis
from singerMovement.singerConstants import (ELEVATOR_GEARBOX_GEAR_RATIO, MAX_TUNER_ROT_ACCEL_DEGPS2, MAX_TUNER_ROT_VEL_DEG_PER_SEC, TUNER_ABS_ENC_OFF_DEG)
from utils.calibration import Calibration
from utils.constants import ELEVATOR_HEIGHT_LEFT_MOTOR_CANID, ELEVATOR_HEIGHT_RIGHT_MOTOR_CANID, TUNER_ANGLE_ABS_POS_ENC
from utils.units import RPM2RadPerSec, deg2Rad, rad2Deg, sign
from utils.signalLogging import log
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from wrappers.wrapperedThroughBoreHexEncoder import WrapperedThroughBoreHexEncoder


# Controls the singer angle motor, including rezeroing from absolute sensors
# and motion profiling
class TunerAngleControl():


    def __init__(self):
        self.NORMAL_POS_DEG = -90.0
        self.AMP_SHOT_POS = 112
        self.MOUNT_OFFSET_DEG = 0.0

        # Singer Rotation Control
        self.motorRight = WrapperedSparkMax(ELEVATOR_HEIGHT_RIGHT_MOTOR_CANID, "SingerRotMotor", brakeMode=False, currentLimitA=20.0)
        self.motorRight.setInverted(False)

        self.kP = Calibration(name="Tuner kP", default=0.1, units="V/degErr")
        self.maxOutputV = Calibration(name="Tuner Max Voltage", default=2.0, units="V")

        #Absolute position sensors
        self.tunerAngleAbsSen = WrapperedThroughBoreHexEncoder(name="tunerAngleAbsPosSen", port=TUNER_ANGLE_ABS_POS_ENC, mountOffsetRad=deg2Rad(-self.MOUNT_OFFSET_DEG))

        self.curPosCmdDeg = 0

        self.curIsTuned = False


    def getAngleDeg(self):
        return rad2Deg(self.tunerAngleAbsSen.getAngleRad())
    
    def setIsAmpShot(self, isTuned):
        self.curIsTuned = isTuned


    def update(self):

        if(self.curIsTuned):
            self.curPosCmdDeg = self.AMP_SHOT_POS
        else:
            self.curPosCmdDeg = self.NORMAL_POS_DEG

        self.tunerAngleAbsSen.update()

        actualPos = self.getAngleDeg()

        err =  self.curPosCmdDeg - actualPos
        
        motorCmdV = err * self.kP.get()

        maxMag = self.maxOutputV.get()

        if(motorCmdV > maxMag):
            motorCmdV = maxMag
        elif(motorCmdV < -maxMag):
            motorCmdV = -maxMag
        
        self.motorRight.setVoltage(motorCmdV)

        log("Tuner Pos Des", self.curPosCmdDeg,"deg")
        log("Tuner Pos Act", actualPos ,"deg")
        log("Tuner Motor Cmd", motorCmdV, "V")
