from rev import CANSparkMax, CANSparkLowLevel
from utils.constants import CLIMBER_MOTOR_LEFT_CANID, CLIMBER_MOTOR_RIGHT_CANID
from wrappers.wrapperedSparkMax import WrapperedSparkMax

class ClimberControl:
    def __init__(self):
        self.winchLeft = WrapperedSparkMax(CLIMBER_MOTOR_LEFT_CANID,"_winchLeft",brakeMode=True)
        self.winchRight = CANSparkMax(CLIMBER_MOTOR_RIGHT_CANID,CANSparkLowLevel.MotorType.kBrushless)
        self.winchRight.setIdleMode(CANSparkMax.IdleMode.kBrake)
        self.winchRight.follow(self.winchLeft.ctrl,True)
        self.cmdVol = 0

    def ctrlWinch(self, cmdIn):
        self.cmdVol = cmdIn

    def update(self):
        if not self.cmdVol == 0:
            self.winchLeft.setVoltage(self.cmdVol)
        else:
            self.winchLeft.setVoltage(0)
