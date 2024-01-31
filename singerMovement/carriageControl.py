#this will be in distance along the elevator, with 0 being at bottom and the top being whatever it is
from singerMovement.singerConstants import GEARBOX_GEAR_RATIO, MAX_CARRIAGE_ACCEL_MPS2, MAX_CARRIAGE_VEL_MPS, MAX_SINGER_ROT_ACCEL_DEGPS2, MAX_SINGER_ROT_VEL_DEG_PER_SEC, SPROCKET_MULTPLICATION_RATIO
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from utils.calibration import Calibration

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



    def update(self):
        pass

        #up/down
    
        #rot
        """
        curSetpoint = ... #  comes in from other code to say where this thing should be physically (in units of meters or degrees or whatever)

        curTime = Timer.getFPGATimestamp()

        if(prevSetpoint != curSetpoint):
        #New setpoint, need to recalcualte the trajectory
        constraints = TrapezoidProfile.Constraints(self.kMaxV, self.kMaxA)
        profile = TrapezoidProfile(constraints, curSetpoint, self.previousProfiledSetpoint)
        self.profileStartTime = curTime 

        curCmdState = profile.calculate(curTime - self.profileStartTime)

        # Use curCmdState.velocity and .position for feedforward and feedback motor control


        self.prevCmdState = curCmdState
    """

    def LinearDispFromMotorRev_SingerUpDown(self):
        self.LinearDisp = self.motorRotations * 1/GEARBOX_GEAR_RATIO * SPROCKET_MULTPLICATION_RATIO
        #when, where, and how do you set how many motor rotations you want?
        return self.LinearDisp
            

    def MotorRevfromLinearDisp_SingerUpDown(self):
        self.motorRotations = self.LinearDisp * 1/SPROCKET_MULTPLICATION_RATIO * GEARBOX_GEAR_RATIO
        #when, where, and how do you set the linear displacement?
        return self.motorRotations
    

    """will need to get command position from the operator controller and
    desired singer angle for autolign"""
    
