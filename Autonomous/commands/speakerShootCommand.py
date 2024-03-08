from wpilib import Timer
from AutoSequencerV2.command import Command
from singerMovement.carriageControl import CarriageControl as cc
from singerMovement.carriageControl import CarriageControlCmd
from pieceHandling.gamepieceHandling import GamePieceHandling as gph

#This is from anywhere? Just shooting into the speaker. It should auto align

class SpeakerShootCommand(Command):
    def __init__(self):
        self.curTime = 0
        self.done = False

    def initialize(self):
        self.startTime = Timer.getFPGATimestamp()

    def execute(self):
        self.curTime = Timer.getFPGATimestamp() - self.startTime

        cc().setPositionCmd(CarriageControlCmd.SUB_SHOT)

        if self.curTime > 1:
            # Intake
            gph().setInput(True, False, False)
        else:
            # Stop intake
            gph().setInput(False, False, False)

    def isDone(self):
        return not gph().getHasGamePiece()
