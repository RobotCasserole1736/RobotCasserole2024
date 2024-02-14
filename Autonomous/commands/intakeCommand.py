from pieceHandling.gamepieceHandling import GamePieceHandling
from AutoSequencerV2.command import Command
from singerMovement.carriageControl import CarriageControl, CarriageControlCmd

class IntakeCommand(Command):
    def __init__(self):
        self.carriageControl = CarriageControl() 
        self.gamePieceHandling = GamePieceHandling()   

    def execute(self):
        self.carriageControl.setPositionCmd(CarriageControlCmd.INTAKE)

        self.gamePieceHandling.setInput(
            False,
            True,
            False
        )

    def isDone(self):
        return False
        #return if we're done. Which should be never? It should be controlled by other things