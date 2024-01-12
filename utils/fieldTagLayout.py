import os
from robotpy_apriltag import AprilTagFieldLayout
from utils.faults import Fault
from utils.singleton import Singleton


class FieldTagLayout(metaclass=Singleton):
    def __init__(self):
        expPath = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "deploy",
                "apriltagLayouts",
                "2023-chargedup.json",
            )
        )
        self.notLoadedFault = Fault(
            f"Apriltag Field Layout could not be loaded from {expPath}"
        )

        try:
            self.fieldTags = AprilTagFieldLayout(path=expPath)
        except Exception: # pylint: disable=broad-exception-caught
            self.fieldTags = None
            self.notLoadedFault.setFaulted()

    def lookup(self, tagId):
        if self.fieldTags is not None:
            return self.fieldTags.getTagPose(tagId)
        else:
            return None
