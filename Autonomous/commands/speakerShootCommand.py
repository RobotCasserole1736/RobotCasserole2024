from AutoSequencerV2.command import Command
from pieceHandling.gamepieceHandling import GamePieceHandling

class SpeakerShootCommand(Command):
    def __init__(self):
        pass

    def execute(self):
        if GamePieceHandling().getHasGamePiece():
            GamePieceHandling().setInput(True,False,False)
            GamePieceHandling().update()

    def isDone(self):
        return not GamePieceHandling().getHasGamePiece()

    def end(self,interrupt):
        GamePieceHandling().setInput(False,False,False)
        GamePieceHandling().update()