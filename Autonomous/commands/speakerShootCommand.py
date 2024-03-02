import wpilib
from AutoSequencerV2.command import Command
from singerMovement.carriageControl import CarriageControl, CarriageControlCmd
from pieceHandling.gamepieceHandling import GamePieceHandling

#This is from anywhere? Just shooting into the speaker. It should auto align

class SpeakerShootCommand(Command):
    def __init__(self):
        self.carriageControl = CarriageControl() 
        self.gamePieceHandling = GamePieceHandling()   

        self.startTime = 0
        self.curTime = 0
        self.done = False
        self.duration = 3

    def initialize(self):
        self.startTime = wpilib.Timer.getFPGATimestamp()

    def execute(self):
        self.carriageControl.setPositionCmd(CarriageControlCmd.SUB_SHOT)

        if self.curTime > 1 :
            self.gamePieceHandling.setInput(
                True,
                False,
                False
            )

        self.curTime = wpilib.Timer.getFPGATimestamp() - self.startTime
        self.done = self.curTime >= self.duration

        if self.done:
            self.gamePieceHandling.setInput(
                False,
                False,
                False
            )

    def isDone(self):
        return self.done
        #return if we're done. Which should be never? It should be controlled by other things