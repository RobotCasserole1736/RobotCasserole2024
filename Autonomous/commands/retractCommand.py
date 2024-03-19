from AutoSequencerV2.command import Command
from pieceHandling.gamepieceHandling import GamePieceHandling
from wpilib import Timer

class RetractCommand(Command):
    def __init__(self):
        self.gamePieceHandling = GamePieceHandling()
        self.duration = 0.4

    def initialize(self):
        self.startTime = Timer.getFPGATimestamp()

    def execute(self):
        # Feedback a little to allow the shooter to work
        self.gamePieceHandling.feedBackSlow(True)

    def isDone(self):
        return (Timer.getFPGATimestamp() - self.startTime) >= self.duration

    def end(self,interrupt):
        self.gamePieceHandling.setInput(False,False,False,False)