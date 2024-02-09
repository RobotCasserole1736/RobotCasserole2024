from gamepieceHandling.gamepieceHandling import GamePieceHandling
from AutoSequencerV2.command import Command

class IntakeCommand(Command):
        
    def execute(self):
        GamePieceHandling.activeIntake

    def isDone(self):
        pass
        #return if we're done. Which should be never? It should be controlled by other things