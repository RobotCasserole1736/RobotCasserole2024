from wpilib import Timer
from wpimath.trajectory import TrapezoidProfile

#Simple wraper for doing motion profiling with the wpilib trapezoid motion profiling
class ProfiledAxis():

    def __init__(self):
        self.curSetpoint = TrapezoidProfile.State()

    # Provide a new desired setpoint position for the profile
    # If this desired setpoint is changed from last call, a new
    # trajectory is calcualted.
    def set(self, newSetpoint, maxVel, maxAccel, curPos, force=False):
        if(newSetpoint != self.curSetpoint or force):
            self.curSetpoint = newSetpoint
            self.profileStartTime = Timer.getFPGATimestamp()
            const = TrapezoidProfile.Constraints(maxVelocity=maxVel, maxAcceleration=maxAccel)
            self.profile = TrapezoidProfile(const,
                                            TrapezoidProfile.State(self.curSetpoint),
                                            TrapezoidProfile.State(position=curPos)
                                            )

    # Get the current velocity/position state of the profile        
    def getCurState(self):
        curTime = Timer.getFPGATimestamp()
        return self.profile.calculate(curTime - self.profileStartTime)
    
    # Check if the profile has hit its end or not
    def isFinished(self):
        curTime = Timer.getFPGATimestamp()
        return self.profile.isFinished(curTime - self.profileStartTime)
