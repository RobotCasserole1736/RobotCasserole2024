#this will be in distance along the elevator, with 0 being at bottom and the top being whatever it is
from singerMovement.singerConstants import GEARBOX_GEAR_RATIO, SPROCKET_MULTPLICATION_RATIO
from wrappers.wrapperedSparkMax import WrapperedSparkMax

class CarriageControl:

    def __init__(self, elevatorMotorCanID, rotMotorCanID):
        self.upDownSingerMotor = WrapperedSparkMax(elevatorMotorCanID, "carriageUpDownMotor", False)
        self.rotSingerMotor = WrapperedSparkMax(rotMotorCanID, "carriageRotMotor", False)

    def update(self):
        pass

    def singerAngle(self, curSingerAngle):
        pass

    def elevatorControl(self, curElevatorHeight):
        pass

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
    
