from rev import CANSparkMax, CANSparkLowLevel
from wpilib import Relay
from wpimath.filter import Debouncer
from utils.constants import CLIMBER_MOTOR_LEFT_CANID, CLIMBER_MOTOR_RIGHT_CANID
from utils.calibration import Calibration
from wrappers.wrapperedSparkMax import WrapperedSparkMax

# needs a sparkmax, relay thing
# the relay thing(?) should basically be a solenoid that automatically 
# braces/locks/something so we stay up when the time is done

class ClimberControl:
    def __init__(self):
        self.ratchetLeft = Relay(0, Relay.Direction.kBothDirections)
        self.ratchetRight = Relay(1, Relay.Direction.kBothDirections)

        self.winchLeft = WrapperedSparkMax(CLIMBER_MOTOR_LEFT_CANID, "_winch")
        self.winchRight = CANSparkMax(CLIMBER_MOTOR_RIGHT_CANID,CANSparkLowLevel.MotorType.kBrushless)
        self.winchRight.setIdleMode(CANSparkMax.IdleMode.kBrake)
        # Set the Right winch to follow the left and invert it
        self.winchRight.follow(self.winchLeft.ctrl, True)

        self.ratchetDebouncerTime = Calibration("RachetDebounce", 0.040, "Seconds")
        self.ratchetDebouncer = Debouncer(
            self.ratchetDebouncerTime.get(), Debouncer.DebounceType.kRising
        )
        self.cmdSpd = 0

    def ctrlWinch(self, cmdIn):
        self.cmdVol = cmdIn

    def lockClimber(self):
        self.ratchetLeft.set(Relay.Value.kOn)
        self.ratchetRight.set(Relay.Value.kOn)

    def unlockClimber(self):
        self.ratchetLeft.set(Relay.Value.kOff)
        self.ratchetRight.set(Relay.Value.kOff)

    def update(self):
        if self.cmdVol is not 0:
            self.unlockClimber()
            if self.ratchetDebouncer.calculate(self.ratchetLeft.get() != Relay.Value.kOn):
                self.winchLeft.setVoltage(self.cmdVol)
            else:
                self.winchLeft.setVoltage(0)
        else:
            self.winchLeft.setVoltage(0)
