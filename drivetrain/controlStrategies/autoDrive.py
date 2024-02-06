import math
from drivetrain.drivetrainCommand import DrivetrainCommand
from drivetrain.drivetrainPhysical import MAX_ROTATE_ACCEL_RAD_PER_SEC_2
from singerMovement.carriageControl import CarriageControl
from wpilib import Timer
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Pose2d
from utils.allianceTransformUtils import onRed, transformX
from utils.calibration import Calibration
from utils.constants import FIELD_LENGTH_FT, SPEAKER_TARGET_HEIGHT_M
from utils.signalLogging import log
from utils.singleton import Singleton
from utils.units import m2ft

class AutoDrive(metaclass=Singleton):
    def __init__(self):
        self.active = False
        self.returnDriveTrainCommand = DrivetrainCommand()
        self.rotKp = Calibration("Auto Align Rotation Kp",1)
        self.rotKd = Calibration("Auto Align Rotation Kd",1)
        self.rotSlewRateLimiter = SlewRateLimiter(
            rateLimit=MAX_ROTATE_ACCEL_RAD_PER_SEC_2
        )

        # Previous Rotation Speed and time for calculating derivative
        self.prevRotError = 0
        self.prevTimeStamp = Timer.getFPGATimestamp()

        # Set speaker coordinates
        self.targetX = transformX(FIELD_LENGTH_FT - m2ft(0.22987))
        self.targetY = 5.4572958333417994

    def setCmd(self, shouldAutoAlign: bool):
        self.active = shouldAutoAlign

    def update(self, cmdIn: DrivetrainCommand, curPose: Pose2d) -> DrivetrainCommand:
        if self.active:
            self.getDesiredSingerAngle(curPose)
            return self.speakerAlign(curPose, cmdIn)
        else:
            return cmdIn

    def getDesiredSingerAngle(self, curPose: Pose2d):
        # Find distance to target
        distX = curPose.X() - self.targetX
        distY = curPose.Y() - self.targetY

        # Get singer height from carriage control
        singerHeight = 1
        targetHeight = SPEAKER_TARGET_HEIGHT_M - singerHeight
        distFromTarget = math.sqrt(math.pow(distX, 2) + math.pow(distY , 2))
        noteTravelPath = math.sqrt(math.pow(targetHeight, 2) + math.pow(distFromTarget , 2))
        self.desiredAngle = math.acos(distFromTarget / noteTravelPath)

        log("Singer Allign desired angle", self.desiredAngle)
        log("Singer Allign DistX, DistY", (distX))
        log("Singer Allign DistY", (distY))

        CarriageControl().setSignerAutoAlignAngle(self.desiredAngle)
        
        

    def speakerAlign(self, curPose: Pose2d, cmdIn: DrivetrainCommand) -> DrivetrainCommand:
        # Update x coord of speaker if necessary
        self.targetX = transformX(m2ft(0.22987))

        # Test to see if we are to the right of the robot
        # If we are, we have to correct the angle by 1 pi
        # This is built into the following equation
        if curPose.X() - self.targetX > 0:
            desAngle = (math.atan((curPose.Y() - self.targetY) / (curPose.X() - self.targetX)) \
                        - math.pi) % (2*math.pi)
            rotError = desAngle - curPose.rotation().radians()
        # If we aren't, we don't need to
        # (these eqations are the same except the other one subtracts by pi and this one doesn't)
        else:
            desAngle = (math.atan((curPose.Y() - self.targetY)/(curPose.X() - self.targetX)) ) \
                        % (2*math.pi)
            rotError = desAngle - curPose.rotation().radians()

        # Test if the angle we calculated will be greater than 180 degrees
        # If it is, reverse it
        if abs(rotError) > math.pi:
            desAngle = ((2* math.pi) - desAngle) * -1
            rotError = ((2* math.pi) - rotError) * -1

        # Check to see if we are making a really small correction
        # If we are, don't worry about it. We only need a certain level of accuracy
        if abs(rotError) <= 0.05:
            rotError = 0
        
        # Calculate derivate of slew-limited angle for feed-forward angular velocity
        rotErrorLimited = self.rotSlewRateLimiter.calculate(desAngle)
        velTCmdDer = (desAngle - self.prevRotError)/(Timer.getFPGATimestamp() - self.prevTimeStamp)

        # Update previous values for next loop
        self.prevRotError = rotErrorLimited
        self.prevTimeStamp = Timer.getFPGATimestamp()

        self.returnDriveTrainCommand.velT = velTCmdDer*self.rotKp.get() + rotError*self.rotKd.get()
        self.returnDriveTrainCommand.velX = cmdIn.velX # Set the X vel to the original X vel
        self.returnDriveTrainCommand.velY = cmdIn.velY # Set the Y vel to the original Y vel
        return self.returnDriveTrainCommand