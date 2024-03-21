from wpilib import Timer
from AutoSequencerV2.command import Command
from pieceHandling.gamepieceHandling import GamePieceHandling

class IntakeCommand(Command):
    def __init__(self):
        pass

    def initialize(self):
        self.startTime = Timer.getFPGATimestamp()

    def execute(self):
        # Intake
        GamePieceHandling().setInput(
            False,
            True,
            False,
            False
        )

    def isDone(self):
        return Timer.getFPGATimestamp() - self.startTime >= 5 or GamePieceHandling().getNoteInPlace()

    def end(self,interrupt):
        GamePieceHandling().setInput(False,False,False,False)
        GamePieceHandling().update()
