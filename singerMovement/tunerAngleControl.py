from math import sin
from singerMovement.profiledAxis import ProfiledAxis
from singerMovement.singerConstants import (ELEVATOR_GEARBOX_GEAR_RATIO, MAX_TUNER_ROT_ACCEL_DEGPS2, MAX_TUNER_ROT_VEL_DEG_PER_SEC, TUNER_ABS_ENC_OFF_DEG)
from utils.calibration import Calibration
from utils.constants import ELEVATOR_HEIGHT_LEFT_MOTOR_CANID, ELEVATOR_HEIGHT_RIGHT_MOTOR_CANID, TUNER_ANGLE_ABS_POS_ENC
from utils.units import RPM2RadPerSec, deg2Rad, rad2Deg, sign
from utils.signalLogging import log
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from wrappers.wrapperedThroughBoreHexEncoder import WrapperedThroughBoreHexEncoder
from humanInterface.operatorInterface import OperatorInterface

# Controls the singer angle motor, including rezeroing from absolute sensors
# and motion profiling
class TunerAngleControl():
    
    Tuner = OperatorInterface()
    
    def __init__(self):
        # Singer Rotation Control
        self.motorRight = WrapperedSparkMax(ELEVATOR_HEIGHT_RIGHT_MOTOR_CANID, "SingerRotMotor", brakeMode=False, currentLimitA=20.0)
        self.motorLeft = WrapperedSparkMax(ELEVATOR_HEIGHT_LEFT_MOTOR_CANID, "SingerRotMotor", brakeMode=False, currentLimitA=20.0)
        #Might need to switch inverted to false.
        self.motorRight.setInverted(True)
        #self.motorLeft.setInverted(True) - Mech. removed this motor from tuner. 
        self.maxV = Calibration(name="Tuner Max Rot Vel", default=MAX_TUNER_ROT_VEL_DEG_PER_SEC, units="degPerSec")
        self.maxA = Calibration(name="Tuner Max Rot Accel", default=MAX_TUNER_ROT_ACCEL_DEGPS2, units="degPerSec2")
        self.profiler = ProfiledAxis() 

        self.kV = Calibration(name="Tuner kV", default=0.045, units="V/rps")
        self.kS = Calibration(name="Tuner kS", default=1.0, units="V")
        self.kG = Calibration(name="Tuner kG", default=0.6, units="V/cos(deg)")
        self.kP = Calibration(name="Tuner kP", default=0.15, units="V/RadErr")
        self.tunerVel = Calibration(name="Tuner Velocity", default=30, units="degPerSec")
        self.motorVelCmd = 0

        #Absolute position sensors
        self.tunerAngleAbsSen = WrapperedThroughBoreHexEncoder(name="tunerAngleAbsPosSen", port=TUNER_ANGLE_ABS_POS_ENC)

        # Absolute Sensor mount offsets
        # After mounting the sensor, these should be tweaked one time
        # in order to adjust whatever the sensor reads into the reference frame
        # of the mechanism
        self.absEncOffsetDeg = TUNER_ABS_ENC_OFF_DEG

        
        self.stopped = True
        self.profiledPos = self.absEncOffsetDeg
        self.curUnprofiledPosCmd = self.absEncOffsetDeg

        

    # Return the rotation of the signer as measured by the absolute sensor in radians
    def _getAbsRot(self):
        return self.tunerAngleAbsSen.getAngleRad() - deg2Rad(self.absEncOffsetDeg)

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
        return motorRev * 1/ELEVATOR_GEARBOX_GEAR_RATIO - self.relEncOffsetRad

    def _angleRadToMotorRad(self, tunerAngleRad):
        return (tunerAngleRad + self.relEncOffsetRad) * ELEVATOR_GEARBOX_GEAR_RATIO 

    def getAngleRad(self):
        motorRot = self.motorRight.getMotorPositionRad()
        tunerAngle = self._motorRadToAngleRad(motorRot)
        return tunerAngle

    # Given the current profiler state, calculate the distance (in radians) needed to stop
    # Uses displacement under constant acceleration equations
    # see https://www.ck12.org/book/ck-12-physics-concepts-intermediate/r3/section/2.6/ 
    # equation 3
    def getStoppingDistanceRad(self): # Uses profiler, nothing calls
        if(self.profiler.isFinished()):
            return 0.0

    def atTarget(self):
        #return self.profiler.isFinished()
        return abs(rad2Deg(self.curUnprofiledPosCmd - self.getAngleRad())) <= 6

    def setDesPos(self, desPos): #Calls _setProfile
        self.stopped = False
        self.curUnprofiledPosCmd = desPos
        self._setProfile(self.curUnprofiledPosCmd)

    def setStopped(self):
        self.stopped = True
        self.curUnprofiledPosCmd = self.getAngleRad()
        #self.profiler.disable()

    def _setProfile(self, desPos): #Uses Profiler, called by setDesPos which is called by nothing
        self.profiler.set(desPos, deg2Rad(self.maxV.get()), deg2Rad(self.maxA.get()), self.getAngleRad())

    def getProfiledDesPos(self):
        return self.profiledPos

    def update(self, getTunerPosCmd):
        actualPos = self.getAngleRad()
        self.tunerAngleAbsSen.update()
        
        if getTunerPosCmd and self.tunerAngleAbsSen.curAngleRad < 1.5:
            desVel = RPM2RadPerSec(self.tunerVel.get())
            self.motorRight.setVelCmd(desVel,self.tunerVel.get()*self.kS.get())
            self.motorLeft.setVelCmd(desVel,self.tunerVel.get()*self.kS.get())
            #print("Tuner is tuning for amp")
            
        elif not getTunerPosCmd and self.tunerAngleAbsSen.curAngleRad > 0:
            desVel = RPM2RadPerSec(self.tunerVel.get())
            self.motorRight.setVelCmd(desVel,self.tunerVel.get()*self.kS.get()*-1)
            self.motorLeft.setVelCmd(desVel,self.tunerVel.get()*self.kS.get()*-1)
            #print("Tuner is tuning for speaker")
            
        else:
            self.motorRight.setVoltage(0.0)
            self.motorLeft.setVoltage(0.0)
            #print("Tuner is not tuning")
        
        # Update motor closed-loop calibration
        if(self.kP.isChanged()):
            self.motorRight.setPID(self.kP.get(), 0.0, 0.0)
            self.motorLeft.setPID(self.kP.get(), 0.0, 0.0)

        if(self.stopped):
            self.motorRight.setVoltage(0.0)
            self.motorLeft.setVoltage(0.0)
            self.profiledPos = actualPos
        else:
            curState = self.profiler.getCurState()

            self.profiledPos = curState.position

            motorPosCmd = self._angleRadToMotorRad(curState.position)

            vFF = self.kV.get() * self.motorVelCmd + self.kS.get() * sign(self.motorVelCmd) \
                - self.kG.get() * sin(actualPos + deg2Rad(15))

            self.motorRight.setPosCmd(motorPosCmd, vFF)
            self.motorLeft.setPosCmd(motorPosCmd, vFF)

        log("Tuner Pos Des", rad2Deg(self.curUnprofiledPosCmd),"deg")
        log("Tuner Pos Profiled", rad2Deg(self.profiledPos) ,"deg")
        log("Tuner Pos Act", rad2Deg(self.tunerAngleAbsSen.curAngleRad) ,"deg")
        log("Tuner Motor Vel Cmd", self.motorVelCmd)
        log("Tuner Abs Sensor",rad2Deg(self.tunerAngleAbsSen.getAngleRad()))