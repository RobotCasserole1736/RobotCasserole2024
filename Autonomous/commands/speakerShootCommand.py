from AutoSequencerV2.command import Command
from pieceHandling.gamepieceHandling import GamePieceHandling

class SpeakerShootCommand(Command):
    def __init__(self):
        pass

    def initialize(self):
        GamePieceHandling().setInput(False,False,False,False)

    def execute(self):
        if GamePieceHandling().getHasGamePiece():
            GamePieceHandling().setInput(True,False,False,True)

    def isDone(self):
        return not GamePieceHandling().getHasGamePiece()

    def end(self,interrupt):
        GamePieceHandling().setInput(False,False,False,False)
