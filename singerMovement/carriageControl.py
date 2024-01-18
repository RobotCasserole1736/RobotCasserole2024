import wpilib 

elevatorUpDown = wpilib.Spark(0)
singerAng = wpilib.spark(1)
                     

class carriageControl():
    
    def __init__(self):
        # Put any one-time init code here
        pass

    def update(self):
        # Put any code that runs every periodic loop here
        pass

    def carriageRot(self, curCarriageAngle):
        pass

    def elevatorControl(self, curElevatorHeight):
        pass

