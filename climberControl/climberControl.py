from wpilib import Relay
from wrappers.wrapperedSparkMax import WrapperedSparkMax

#needs a sparkmax, relay thing
#the relay thing(?) should basically be a solenoid that automatically braces/locks/something so we stay up when the time is done

class climberControl():
    def __init__(self, canID):
        self.relay = Relay(0,Relay.Direction(0))
        self.winch = WrapperedSparkMax(canID , "_winch")
 
    # Not sure if needed
    # def getValue(self):
    #     return self.relay.get()

    def ctrlWinch(self, In):
        self.winch.setVelCmd(In)

    def setRachet(self, State):
        if self.relay.get() != State:
            self.relay.set(State)