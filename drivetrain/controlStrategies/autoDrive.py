import math
from wpilib import Timer
from wpimath.filter import SlewRateLimiter
from wpimath.geometry import Pose2d, Rotation2d, Translation2d
from drivetrain.drivetrainCommand import DrivetrainCommand
from drivetrain.drivetrainPhysical import MAX_ROTATE_ACCEL_RAD_PER_SEC_2
from singerMovement.carriageControl import CarriageControl
from utils.allianceTransformUtils import transformX
from utils.calibration import Calibration
from utils.constants import SPEAKER_TARGET_HEIGHT_M, \
    AMP_LOC_X_M, AMP_LOC_Y_M, SPEAKER_LOC_X_M, SPEAKER_LOC_Y_M
from utils.signalLogging import log
from utils.singleton import Singleton
from singerMovement.elevatorHeightControl import ElevatorHeightControl

class AutoDrive(metaclass=Singleton):
    def __init__(self):
        self.speakerAlignActive = False
        self.returnDriveTrainCommand = DrivetrainCommand()
        self.rotKp = Calibration("Auto Align Rotation Kp",3)
        self.maxRotSpd = Calibration("Auto Align Max Rotate Speed", 4)

        # Previous Rotation Speed and time for calculating derivative
        self.prevDesAngle = 0
        self.prevTimeStamp = Timer.getFPGATimestamp()

        # Set speaker coordinates
        self.speakerX = transformX(SPEAKER_LOC_X_M)
        self.speakerY = SPEAKER_LOC_Y_M

        # Set Amp coordinates
        self.ampX = transformX(AMP_LOC_X_M)
        self.ampY = AMP_LOC_Y_M

        self.desiredAngle = 0

    def setSpeakerAutoAlignCmd(self, shouldAutoAlign: bool):
        self.speakerAlignActive = shouldAutoAlign

    def setAmpAutoAlignCmd(self, shouldAutoAlign: bool):
        self.ampAlignActive = shouldAutoAlign

    def update(self, cmdIn: DrivetrainCommand, curPose: Pose2d) -> DrivetrainCommand:
        if self.speakerAlignActive:
           # self.getDesiredSingerAngle(curPose)
            return self.calcSpeakerDrivetrainCommand(curPose, cmdIn)
        else:
            return cmdIn

    def getDesiredSingerAngle(self, curPose: Pose2d):
        # Find distance to target
        distX = curPose.X() - transformX(self.speakerX)
        distY = curPose.Y() - self.speakerY

        # Get singer height from carriage control
        singerHeight = ElevatorHeightControl().getHeightM()
        targetHeight = SPEAKER_TARGET_HEIGHT_M - singerHeight
        distFromTarget = math.sqrt(math.pow(distX, 2) + math.pow(distY , 2))
        noteTravelPath = math.sqrt(math.pow(targetHeight, 2) + math.pow(distFromTarget , 2))
        self.desiredAngle = math.acos(distFromTarget / noteTravelPath)

        log("Singer Allign desired angle", self.desiredAngle)
        log("Singer Allign DistX, DistY", (distX))
        log("Singer Allign DistY", (distY))

        CarriageControl().setSignerAutoAlignAngle(self.desiredAngle)

    def getRotationAngle(self, curPose: Pose2d) -> Rotation2d:
        targetLocation = Translation2d(transformX(self.speakerX),self.speakerY)
        robotToTargetTrans = targetLocation - curPose.translation()
        return Rotation2d(robotToTargetTrans.X(), robotToTargetTrans.Y())

    def calcSpeakerDrivetrainCommand(self, curPose: Pose2d, cmdIn: DrivetrainCommand) -> DrivetrainCommand:
        # Find difference between robot angle and angle facing the speaker
        rotError = self.getRotationAngle(curPose) - curPose.rotation()

        # Check to see if we are making a really small correction
        # If we are, don't worry about it. We only need a certain level of accuracy
        if abs(rotError.radians()) <= 0.05:
            rotError = 0
        else:
            rotError = rotError.radians()

        self.returnDriveTrainCommand.velT = min(rotError*self.rotKp.get(),self.maxRotSpd.get())
        self.returnDriveTrainCommand.velX = cmdIn.velX # Set the X vel to the original X vel
        self.returnDriveTrainCommand.velY = cmdIn.velY # Set the Y vel to the original Y vel
        return self.returnDriveTrainCommand
