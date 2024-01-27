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
        #self.hold = Calibration("ClimberHoldVoltage" , 1 , "Volts" , 0 , 12) 

    def ctrlWinch(self, In):
        #Rachet Engaged = 0
        #Rachet Disengaged = 1
        if In == 0 and self.ratchet.get() == 1:
            self.ratchet.set(Relay.Value(0))
        
        if self.ratchetDebouncer.calculate(self.ratchet.get() != Relay.Value(1)):
            self.ratchet.set(Relay.Value(1))
            self.winch.setVoltage(In * 12)
                
        

    # def setRachet(self, State):
    #     self.relay.set(State)