import wpilib
from AutoSequencerV2.command import Command
from singerMovement.carriageControl import CarriageControl, CarriageControlCmd
from pieceHandling.gamepieceHandling import GamePieceHandling

class SpeakerShootCommand(Command):
    def __init__(self):
        self.carriageControl = CarriageControl()
        self.gamePieceHandling = GamePieceHandling()

        self.startTime = 0
        self.curTime = 0
        self.done = False
        self.duration = 3
        self.posCommanded = False

    def initialize(self):
        self.startTime = wpilib.Timer.getFPGATimestamp()

    def execute(self):
        if not self.posCommanded:
            #self.carriageControl.setPositionCmd(CarriageControlCmd.SUB_SHOT)
            self.posCommanded = True

        self.curTime = wpilib.Timer.getFPGATimestamp() - self.startTime
        self.gamePieceHandling.update()

        """
        # Start Shooting
        if self.curTime > 1:
            self.gamePieceHandling.setInput(True,False,False)
        """
        self.gamePieceHandling.setInput(True,False,False)

        # Stop Shooting
        if self.curTime > self.duration:
            self.gamePieceHandling.setInput(False,False,False)
            self.gamePieceHandling.update()
            self.done = True

    def isDone(self):
        return self.done
    
    def end(self,interrupt):
        self.gamePieceHandling.setInput(False,False,False)