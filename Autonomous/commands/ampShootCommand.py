from AutoSequencerV2.command import Command
from singerMovement.carriageControl import CarriageControl, CarriageControlCmd
from pieceHandling.gamepieceHandling import GamePieceHandling

class EjectCommand(Command):
    def __init__(self):
        self.carriageControl = CarriageControl() 
        self.gamePieceHandling = GamePieceHandling()   

    def execute(self):
        self.carriageControl.setPositionCmd(CarriageControlCmd.AMP)

        self.gamePieceHandling.setInput(
            True,
            False,
            False
        )

    def isDone(self):
        return False
        #return if we're done. Which should be never? It should be controlled by other things