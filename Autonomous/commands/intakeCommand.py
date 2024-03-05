import wpilib
from pieceHandling.gamepieceHandling import GamePieceHandling
from AutoSequencerV2.command import Command
from singerMovement.carriageControl import CarriageControl, CarriageControlCmd

class IntakeCommand(Command):
    def __init__(self):
        self.carriageControl = CarriageControl() 
        self.gamePieceHandling = GamePieceHandling()   
        self.startTime = 0
        self.curTime = 0
        self.done = False

    def initialize(self):
        self.startTime = wpilib.Timer.getFPGATimestamp()

    def execute(self):
        self.curTime = wpilib.Timer.getFPGATimestamp() - self.startTime

        self.carriageControl.setPositionCmd(CarriageControlCmd.INTAKE)

        self.gamePieceHandling.setInput(
            False,
            True,
            False
        )

        if GamePieceHandling.getHasGamePiece:
            self.done = True
        
        if self.done:
            self.gamePieceHandling.setInput(
                False,
                False,
                False
            )

    def isDone(self):
        return False
        #return if we're done. Which should be never? It should be controlled by other things