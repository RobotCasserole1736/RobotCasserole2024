from AutoSequencerV2.mode import Mode
from Autonomous.commands.speakerShootCommand import SpeakerShootCommand

# Just drives out of the starting zone. That's all.
class justShoot(Mode):
    def __init__(self):
        Mode.__init__(self, f"Just Shoot")
        self.shoot = SpeakerShootCommand()

    def getCmdGroup(self):
        # Just return the path command
        return self.shoot