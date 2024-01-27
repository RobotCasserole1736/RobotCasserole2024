from wpilib import Relay
from wpimath.filter import Debouncer
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from utils.calibration import Calibration
#needs a sparkmax, relay thing
#the relay thing(?) should basically be a solenoid that automatically braces/locks/something so we stay up when the time is done

class climberControl():
    def __init__(self, canID):
        self.ratchet = Relay(0,Relay.Direction(0))
        self.winch = WrapperedSparkMax(canID , "_winch")
        self.ratchetDebouncerTime = Calibration("RachetDebounce" , .040 , "Seconds")
        self.ratchetDebouncer = Debouncer(self.ratchetDebouncerTime.get() , Debouncer.DebounceType(2))

    def ctrlWinch(self, In):
        if self.ratchetDebouncer.calculate(self.ratchet.get() != Relay.Value(1)):
            self.ratchet.set(Relay.Value(1))
            self.winch.setVoltage(In * 12)
        else:
            self.ratchet.set(Relay.Value(0))
            