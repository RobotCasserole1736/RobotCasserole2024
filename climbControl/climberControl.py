from rev import CANSparkMax, CANSparkLowLevel
from wpilib import Relay
from utils.constants import CLIMBER_MOTOR_LEFT_CANID, CLIMBER_MOTOR_RIGHT_CANID
from wrappers.wrapperedSparkMax import WrapperedSparkMax

class ClimberControl:
    def __init__(self):
        self.ratchetLeft = Relay(0, Relay.Direction.kBothDirections)
        self.ratchetRight = Relay(1, Relay.Direction.kBothDirections)
        self.winchLeft = WrapperedSparkMax(CLIMBER_MOTOR_LEFT_CANID, "_winch")
        self.winchRight = CANSparkMax(CLIMBER_MOTOR_RIGHT_CANID,CANSparkLowLevel.MotorType.kBrushless)
        self.winchRight.setIdleMode(CANSparkMax.IdleMode.kBrake)
        # Set the Right winch to follow the left and invert it
        self.winchRight.follow(self.winchLeft.ctrl, True)
        self.cmdVol = 0

    def ctrlWinch(self, cmdIn):
        self.cmdVol = cmdIn

    def lockClimber(self):
        self.ratchetLeft.set(Relay.Value.kOn)
        self.ratchetRight.set(Relay.Value.kOn)

    def unlockClimber(self):
        self.ratchetLeft.set(Relay.Value.kOff)
        self.ratchetRight.set(Relay.Value.kOff)

    def update(self):
        if not self.cmdVol == 0:
            self.unlockClimber()
            self.winchLeft.setVoltage(self.cmdVol)
        else:
            self.lockClimber()
            self.winchLeft.setVoltage(0)
