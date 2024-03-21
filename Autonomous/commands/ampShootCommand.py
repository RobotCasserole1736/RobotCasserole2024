from AutoSequencerV2.command import Command
from pieceHandling.gamepieceHandling import GamePieceHandling

class EjectCommand(Command):
    def __init__(self):
        pass

    def execute(self):
        #self.carriageControl.setPositionCmd(CarriageControlCmd.AMP)

        GamePieceHandling().setInput(
            True,
            False,
            False,
            False
        )

    def isDone(self):
        # return if we're done. Which should be never? It should be controlled by other things
        return False