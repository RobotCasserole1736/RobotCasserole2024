import wpilib
from AutoSequencerV2.command import Command
from singerMovement.carriageControl import CarriageControl, CarriageControlCmd
from pieceHandling.gamepieceHandling import GamePieceHandling

class SpeakerShootCommand(Command):
    def __init__(self):
        self.carriageControl = CarriageControl()
        self.gamePieceHandling = GamePieceHandling()

        self.startTime = 0
        self.curTime = 0
        self.done = False
        self.duration = 3

    def initialize(self):
        self.startTime = wpilib.Timer.getFPGATimestamp()

    def execute(self):
        self.curTime = wpilib.Timer.getFPGATimestamp() - self.startTime
        self.done = self.curTime >= self.duration
        self.carriageControl.setPositionCmd(CarriageControlCmd.SUB_SHOT)
        self.gamePieceHandling.update()

        # Start Shooting
        if self.curTime > 1:
            self.gamePieceHandling.setInput(True,False,False)

        # Stop Shooting
        if self.done:
            self.gamePieceHandling.setInput(False,False,False)

    def isDone(self):
        self.gamePieceHandling.setInput(False,False,False)
        return self.done