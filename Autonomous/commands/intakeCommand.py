import wpilib
from pieceHandling.gamepieceHandling import GamePieceHandling as gph
from AutoSequencerV2.command import Command
from singerMovement.carriageControl import CarriageControl as cc
from singerMovement.carriageControl import CarriageControlCmd

class IntakeCommand(Command):
    def __init__(self):
        pass

    def execute(self):
        cc().setPositionCmd(CarriageControlCmd.INTAKE)

        """if self.gamePieceHandling.getHasGamePiece:
            self.done = True"""
        gph().setInput(False, True, False)

    def isDone(self):
        return gph().getHasGamePiece()