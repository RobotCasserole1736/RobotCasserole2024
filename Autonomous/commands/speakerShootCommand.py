from AutoSequencerV2.command import Command
from wpilib import Timer
from pieceHandling.gamepieceHandling import GamePieceHandling as gph
from singerMovement.carriageControl import CarriageControl as cc
from singerMovement.carriageControl import CarriageControlCmd

#This is from anywhere? Just shooting into the speaker. It should auto align

class SpeakerShootCommand(Command):
    def __init__(self):
        self.curTime = 0
        self.startTime = Timer.getFPGATimestamp()
        self.posCommanded = False

    def execute(self):
        self.curTime = Timer.getFPGATimestamp() - self.startTime

        if not self.posCommanded:
            cc().setPositionCmd(CarriageControlCmd.SUB_SHOT)
            self.posCommanded = True

        if self.curTime > 1:
            # Shoot
            gph().setInput(True, False, False)
        else:
            # Stop shooting
            gph().setInput(False, False, False)

    def isDone(self):
        return not gph().getHasGamePiece()
