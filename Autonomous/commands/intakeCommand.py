from AutoSequencerV2.command import Command
from pieceHandling.gamepieceHandling import GamePieceHandling

class IntakeCommand(Command):
    def __init__(self):
        self.gamePieceHandling = GamePieceHandling()

    def execute(self):
        # Intake
        self.gamePieceHandling.setInput(
            False,
            True,
            False
        )

    def isDone(self):
        return self.gamePieceHandling.getNoteInPlace()

    def end(self,interrupt):
        self.gamePieceHandling.setInput(False,False,False)
        self.gamePieceHandling.update()