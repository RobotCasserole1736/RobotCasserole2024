from AutoSequencerV2.command import Command
from pieceHandling.gamepieceHandling import GamePieceHandling
from singerMovement.carriageControl import CarriageControl, CarriageControlCmd

class IntakeCommand(Command):
    def __init__(self):
        self.carriageControl = CarriageControl()
        self.gamePieceHandling = GamePieceHandling()

    def execute(self):
        self.carriageControl.setPositionCmd(CarriageControlCmd.INTAKE)

        # Intake
        self.gamePieceHandling.setInput(
            False,
            True,
            False
        )

    def isDone(self):
        return self.gamePieceHandling.getNoteInPlace()