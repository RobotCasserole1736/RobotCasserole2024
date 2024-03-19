from wpilib import Timer
from AutoSequencerV2.command import Command
from pieceHandling.gamepieceHandling import GamePieceHandling

class IntakeCommand(Command):
    def __init__(self):
        self.gamePieceHandling = GamePieceHandling()

    def initialize(self):
        self.startTime = Timer.getFPGATimestamp()

    def execute(self):
        # Intake
        self.gamePieceHandling.setInput(False,True,False)

    def isDone(self):
        return Timer.getFPGATimestamp() - self.startTime >= 3

    def end(self,interrupt):
        self.gamePieceHandling.setInput(False,False,False)
        self.gamePieceHandling.update()