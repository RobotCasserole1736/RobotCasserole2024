import wpilib
from pieceHandling.gamepieceHandling import GamePieceHandling
from AutoSequencerV2.command import Command
from singerMovement.carriageControl import CarriageControl, CarriageControlCmd

class IntakeCommand(Command):
    def __init__(self):
        self.carriageControl = CarriageControl() 
        self.gamePieceHandling = GamePieceHandling()   
        self.done = False
        self.hasRan = False
        #self.gamePieceHandling.setInput(False, True, False)

    def execute(self):
        self.carriageControl.setPositionCmd(CarriageControlCmd.INTAKE)

        """if self.gamePieceHandling.getHasGamePiece:
            self.done = True"""
        
        if self.done:
            self.gamePieceHandling.setInput(
                False,
                False,
                False
            )
            #self.gamePieceHandling.updateIntake(False)
            #self.gamePieceHandling.updateFloorRoller(False)
        else:
            self.gamePieceHandling.setInput(
                False,
                True,
                False
            )
            self.hasRan = True

        self.gamePieceHandling.update()
    
    def isDone(self):
        return (self.done and self.hasRan)
        #return if we're done. Which should be never? It should be controlled by other things