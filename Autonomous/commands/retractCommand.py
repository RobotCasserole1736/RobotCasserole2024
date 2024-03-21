from AutoSequencerV2.command import Command
from pieceHandling.gamepieceHandling import GamePieceHandling
from wpilib import Timer

class RetractCommand(Command):
    def __init__(self):
        self.duration = 0.4

    def initialize(self):
        self.startTime = Timer.getFPGATimestamp()

    def execute(self):
        # Feedback a little to allow the shooter to work
        GamePieceHandling().feedBackSlow(True)

    def isDone(self):
        return (Timer.getFPGATimestamp() - self.startTime) >= self.duration

    def end(self,interrupt):
        GamePieceHandling().setInput(False,False,False,False)