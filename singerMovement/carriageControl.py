#this will be in distance along the elevator, with 0 being at bottom and the top being whatever it is
from wpilib import Timer
from singerMovement.singerConstants import GEARBOX_GEAR_RATIO, MAX_CARRIAGE_ACCEL_MPS2, MAX_CARRIAGE_VEL_MPS, MAX_SINGER_ROT_ACCEL_DEGPS2, MAX_SINGER_ROT_VEL_DEG_PER_SEC, SPROCKET_MULTPLICATION_RATIO
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from utils.calibration import Calibration
from wpimath.geometry import Pose2d
from drivetrain.poseEstimation.drivetrainPoseEstimator import DrivetrainPoseEstimator
from wpimath.trajectory import TrapezoidProfile

class CarriageControl:

    def __init__(self, elevatorMotorCanID, rotMotorCanID):
        #up/down
        self.upDownSingerMotor = WrapperedSparkMax(elevatorMotorCanID, "carriageUpDownMotor", False)
        self.kMaxVUpDown = Calibration(name="Max Vel of Carriage up/down", default=MAX_CARRIAGE_VEL_MPS)
        self.kMaxAUpDown = Calibration(name="Max Acceleration of Carriage up/down", default=MAX_CARRIAGE_ACCEL_MPS2)

        #rot
        self.rotSingerMotor = WrapperedSparkMax(rotMotorCanID, "carriageRotMotor", False)
        self.kMaxVRot = Calibration(name="Max Vel of Carriage singer rot", default=MAX_SINGER_ROT_VEL_DEG_PER_SEC)
        self.kMaxARot = Calibration(name="Max Acceleration of Carriage singer rot", default=MAX_SINGER_ROT_ACCEL_DEGPS2)

        self.constraints = TrapezoidProfile.Constraints(maxVelocity=self.kMaxVUpDown.get(), maxAcceleration=self.kMaxAUpDown.get())

        #self.curSetpoint = can't be drivetrain because it's just carriage?
        self.prevProfiledSetpoint = DrivetrainPoseEstimator.getCurEstPose



    def update(self):
        pass
        """
        #up/down
        #curSetpoint = can't be drivetrain setpoint because it's carriage?
        curTime = Timer.getFPGATimestamp()

        if(self.prevProfiledSetpoint != self.curSetpoint):
            #new setpoint, need to recalculate trajectory
            profile = TrapezoidProfile(self.constraints,curSetpoint,self.prevProfiledSetpoint)
            self.profileStartTime = curTime

        curCmdState = profile.calculate(curTime - self.profileStartTime)
        # Use curCmdState.velocity and .position for feedforward and feedback motor control

        self.prevCmdState = curCmdState
        """

        #rot

    """

    def LinearDispFromMotorRev_SingerUpDown(self):
        self.LinearDisp = self.motorRotations * 1/GEARBOX_GEAR_RATIO * SPROCKET_MULTPLICATION_RATIO
        #when, where, and how do you set how many motor rotations you want?
        return self.LinearDisp
            

    def MotorRevfromLinearDisp_SingerUpDown(self):
        self.motorRotations = self.LinearDisp * 1/SPROCKET_MULTPLICATION_RATIO * GEARBOX_GEAR_RATIO
        #when, where, and how do you set the linear displacement?
        return self.motorRotations
    

    will need to get command position from the operator controller and
    desired singer angle for autolign"""

    def singerAutoAlignment(self, desiredAngle):
        # TODO Move elevator set amount

        # TODO take desired angle from autoDrive and set singer rotation to be said angle

        return
    
