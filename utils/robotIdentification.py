#The goal of this file is to identify which robot is currently running the code.
#The constants between practice and main robots may be different. 
import wpilib
import ntcore as nt
from utils.signalLogging import log
from enum import Enum
from utils.singleton import Singleton
RobotTypes = Enum('RobotTypes', ['Main','Practice','TestBoard'])

class RobotIdentification(metaclass=Singleton):

    def __init__(self):
        self.roboControl = wpilib.RobotController
        self.robotType = RobotTypes.Main
        
        
    def configureValue(self):
        if self.roboControl.getSerialNumber() == 1: #Im assuming the normal robot's serial number is 1 rn. I will fix later
            self.robotType = RobotTypes.Main 
        elif self.roboControl.getSerialNumber() == 2:  #Im assuming the test robot's serial number is 2 rn. I will fix later
            self.robotType = RobotTypes.Practice
        elif str(self.roboControl.getSerialNumber()) == "0316b37C":  #Test to see if the RoboRio serial number is our testboard's serial number.
            self.robotType = RobotTypes.TestBoard
        else:
            #If the Robo Rio's serial number is not equal to any of our known serial numbers, assume we are the main robot
            self.robotType = RobotTypes.Main
        #log("RoboRio Serial Number", self.roboControl.getSerialNumber(), "num")
        log("RoboRioSerialNumber", self.robotType)
        
            
    def getRobotType(self):
        return self.robotType 


