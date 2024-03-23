from wpilib import Timer
from AutoSequencerV2.command import Command
from pieceHandling.gamepieceHandling import GamePieceHandling

class IntakeCommand(Command):
    def __init__(self):
        self.gamePieceHandling = GamePieceHandling()
        self.duration = 3

    def initialize(self):
        self.startTime = Timer.getFPGATimestamp()

    def execute(self):
        # Intake
        self.gamePieceHandling.setInput(
            False,
            True,
            False,
            False
        )
        
    def maxDuration(self, duration):
        self.duration = duration + 1

    def isDone(self):
        return Timer.getFPGATimestamp() - self.startTime >= self.duration #or self.gamePieceHandling.getNoteInPlace()

    def end(self,interrupt):
        self.gamePieceHandling.setInput(False,False,False,False)
        self.gamePieceHandling.update()