from wpilib import Timer
from wpimath.trajectory import TrapezoidProfile

#Simple wraper for doing motion profiling with the wpilib trapezoid motion profiling
class ProfiledAxis():

    def __init__(self):
        self.curSetpoint = TrapezoidProfile.State()
        self.profile = None

        self.profileStartTime = Timer.getFPGATimestamp()

    # Provide a new desired setpoint position for the profile
    # If this desired setpoint is changed from last call, a new
    # trajectory is calcualted.
    def set(self, newSetpoint, maxVel, maxAccel, curPos):
        if(newSetpoint != self.curSetpoint or self.profile is None):
            self.restartProfile(newSetpoint, maxVel, maxAccel,curPos)

    def disable(self):
        self.profile = None
            
    def restartProfile(self, newSetpoint, maxVel, maxAccel, curPos):
        const = TrapezoidProfile.Constraints(maxVelocity=maxVel, maxAcceleration=maxAccel)

        if(self.profile is not None and not self.isFinished()):
            # Profile was already running, use its current velocity as the start poitn
            initState = self.getCurState()
        else:
            initState = TrapezoidProfile.State(curPos, 0.0)

        self.curSetpoint = newSetpoint
        self.profileStartTime = Timer.getFPGATimestamp()
        self.profile = TrapezoidProfile(const,
                                        TrapezoidProfile.State(self.curSetpoint),
                                        initState
                                        )
            
    # Get the current velocity/position state of the profile        
    def getCurState(self):
        if(self.profile is not None):
            curTime = Timer.getFPGATimestamp()
            return self.profile.calculate(curTime - self.profileStartTime)
        else:
            return TrapezoidProfile.State()
    
    # Check if the profile has hit its end or not
    def isFinished(self):
        if(self.profile is not None):
            curTime = Timer.getFPGATimestamp()
            return self.profile.isFinished(curTime - self.profileStartTime)
        else:
            return True
