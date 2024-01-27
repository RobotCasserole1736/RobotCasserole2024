from wpilib import Relay
from wpimath.filter import Debouncer
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from utils.calibration import Calibration

# needs a sparkmax, relay thing
# the relay thing(?) should basically be a solenoid that automatically braces/locks/something so we stay up when the time is done


class climberControl:
    def __init__(self, canID):
        self.ratchet = Relay(0, Relay.Direction(0))
        self.winch = WrapperedSparkMax(canID, "_winch")
        self.ratchetDebouncerTime = Calibration("RachetDebounce", 0.040, "Seconds")
        self.ratchetDebouncer = Debouncer(
            self.ratchetDebouncerTime.get(), Debouncer.DebounceType(2)
        )
        self.cmdSpd = 0

    def ctrlWinch(self, cmdIn):
        self.cmdSpd = cmdIn

    def update(self):
        if self.ratchetDebouncer.calculate(
            self.ratchet.get() != Relay.Value(1)
        ):  # TODO - how does self.rachet get set to 1?
            self.ratchet.set(Relay.Value(1))
            self.winch.setVoltage(self.cmdSpd * 12)
        else:
            self.ratchet.set(Relay.Value(0))
