from wpilib import Timer
from wpimath.trajectory import TrapezoidProfile


class ProfiledAxis():

    def __init__(self):
        self.curSetpoint = TrapezoidProfile.State()

    def set(self, newSetpoint, maxVel, maxAccel, curPos):
        if(newSetpoint != self.curSetpoint):
            self.profileStartTime = Timer.getFPGATimestamp()
            self.curSetpoint = newSetpoint
            const = TrapezoidProfile.Constraints(maxVelocity=maxVel, maxAcceleration=maxAccel)
            self.profile = TrapezoidProfile(const,
                                            TrapezoidProfile.State(self.curSetpoint),
                                            TrapezoidProfile.State(position=curPos)
                                            )
            
    def getCurState(self):
        curTime = Timer.getFPGATimestamp()
        return self.profile.calculate(curTime - self.profileStartTime)
    
    def isFinished(self):
        curTime = Timer.getFPGATimestamp()
        return self.profile.isFinished(curTime - self.profileStartTime)
