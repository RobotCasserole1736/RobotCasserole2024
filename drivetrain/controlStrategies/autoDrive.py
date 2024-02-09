import math
from wpilib import Timer
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Pose2d, Rotation2d, Translation2d
from utils.allianceTransformUtils import onRed, transformX
from wpimath.geometry import Pose2d
from drivetrain.drivetrainCommand import DrivetrainCommand
from drivetrain.drivetrainPhysical import MAX_ROTATE_ACCEL_RAD_PER_SEC_2
from singerMovement.carriageControl import CarriageControl
from utils.allianceTransformUtils import transformX #and onRed,
from utils.calibration import Calibration
from utils.constants import SPEAKER_TARGET_HEIGHT_M
from utils.signalLogging import log
from utils.singleton import Singleton

class AutoDrive(metaclass=Singleton):
    def __init__(self):
        self.active = False
        self.returnDriveTrainCommand = DrivetrainCommand()
        self.rotKp = Calibration("Auto Align Rotation Kp",2)
        self.rotKd = Calibration("Auto Align Rotation Kd",3)
        self.rotSlewRateLimiter = SlewRateLimiter(
            rateLimit=MAX_ROTATE_ACCEL_RAD_PER_SEC_2
        )

        # Previous Rotation Speed and time for calculating derivative
        self.prevDesAngle = 0
        self.prevTimeStamp = Timer.getFPGATimestamp()

        # Set speaker coordinates
        self.targetX = transformX(0.22987)
        self.targetY = 5.4572958333417994

        self.desiredAngle = 0

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

    def getRotationAngle(self, curPose: Pose2d) -> Rotation2d:
        targetLocation = Translation2d(transformX(self.targetX),self.targetY)
        robotToTargetTrans = targetLocation - curPose.translation()
        return Rotation2d(robotToTargetTrans.X(), robotToTargetTrans.Y())

    def speakerAlign(self, curPose: Pose2d, cmdIn: DrivetrainCommand) -> DrivetrainCommand:
        rotError2d = self.getRotationAngle(curPose) - curPose.rotation()

        # Check to see if we are making a really small correction
        # If we are, don't worry about it. We only need a certain level of accuracy
        if abs(rotError2d.radians()) <= 0.05:
            rotError = 0
        else:
            rotError = rotError2d.radians()

        targetLocation = Translation2d(transformX(self.targetX),self.targetY)
        desAngle = Rotation2d(targetLocation.X(),targetLocation.Y()).radians()

        # Calculate derivate of slew-limited angle for feed-forward angular velocity
        desAngleLimited = self.rotSlewRateLimiter.calculate(desAngle)
        velTCmdDer = (desAngleLimited - self.prevDesAngle)/(Timer.getFPGATimestamp() - self.prevTimeStamp)

        # Update previous values for next loop
        self.prevDesAngle = desAngleLimited
        self.prevTimeStamp = Timer.getFPGATimestamp()

        self.returnDriveTrainCommand.velT = rotError*self.rotKp.get() + velTCmdDer*self.rotKd.get()
        self.returnDriveTrainCommand.velX = cmdIn.velX # Set the X vel to the original X vel
        self.returnDriveTrainCommand.velY = cmdIn.velY # Set the Y vel to the original Y vel
        return self.returnDriveTrainCommand