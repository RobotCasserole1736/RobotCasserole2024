from AutoSequencerV2.mode import Mode
from Autonomous.commands.intakeCommand import IntakeCommand


# Just drives out of the starting zone. That's all.
class IntakeTest(Mode):
    def __init__(self):
        Mode.__init__(self, f"IntakeTest")
        self.intake = IntakeCommand()

    def getCmdGroup(self):
        # Just return the path command
        return self.intake