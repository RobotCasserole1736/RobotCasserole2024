from wpilib import Relay
from wpimath.filter import Debouncer
from utils import constants
from utils.calibration import Calibration
from wrappers.wrapperedSparkMax import WrapperedSparkMax

# needs a sparkmax, relay thing
# the relay thing(?) should basically be a solenoid that automatically 
# braces/locks/something so we stay up when the time is done

class ClimberControl:
    def __init__(self):
        #TODO - add second Relay, since we have one on each climber motor
        #TODO - Second arg of constructor should be something like Relay.Direction.kForward
        self.ratchet = Relay(0, Relay.Direction(0))
        #TODO - Add second/right motor controller. One should be inverted, and probably follow the first
        self.winch = WrapperedSparkMax(constants.CLIMBER_MOTOR_LEFT_CANID, "_winch")
        self.ratchetDebouncerTime = Calibration("RachetDebounce", 0.040, "Seconds")
        self.ratchetDebouncer = Debouncer(
            #TODO - change second argument here to something like Debouncer.DebounceType.kRising
            self.ratchetDebouncerTime.get(), Debouncer.DebounceType(2)
        )
        self.cmdSpd = 0

    def ctrlWinch(self, cmdIn):
        self.cmdSpd = cmdIn

    def update(self):
        if self.ratchetDebouncer.calculate(
            self.ratchet.get() != Relay.Value(1)
        ):  # TODO - how does self.rachet get set to 1?
            #TODO - set should take a value like Relay.Value.kOn
            self.ratchet.set(Relay.Value(1))
            self.winch.setVoltage(self.cmdSpd * 12)
            #TODO - set voltage of second motor if it's not following the first. If it is, nothing needed
        else:
            #TODO - set should take an argument like Relay.Value.kOff
            self.ratchet.set(Relay.Value(0))
            #TODO - be sure to set motor voltage to 0 here (both motors if one is not following)!
