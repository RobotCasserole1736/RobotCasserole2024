from AutoSequencerV2.command import Command
from singerMovement.carriageControl import CarriageControl, CarriageControlCmd
from pieceHandling.gamepieceHandling import GamePieceHandling

class SpeakerShootCommand(Command):
    def __init__(self):
        self.gamePieceHandling = GamePieceHandling()

    def execute(self):
        if self.gamePieceHandling.getHasGamePiece():
            self.gamePieceHandling.setInput(True,False,False)
            self.gamePieceHandling.update()

    def isDone(self):
        return not self.gamePieceHandling.getHasGamePiece()

    def end(self,interrupt):
        self.gamePieceHandling.setInput(False,False,False)