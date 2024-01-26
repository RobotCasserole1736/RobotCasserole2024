#Priorities
#1. Read the rest of the documentation for ToF 
#2. Take a look at SparkMax stuff
#3. Ask about playing with fusion and how to implement and if did classes correct
#4. Get information from Operator control block on architecture

#Resources: https://robotpy.readthedocs.io/projects/pwfusion/en/latest/playingwithfusion/TimeOfFlight.html


#import all we need
from wpilib import PWMSparkMax
from utils.calibration import Calibration
from utils import constants
from utils.units import RPM2RadPerSec
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from playingwithfusion import TimeOfFlight


class gamepieceHandling:
    def __init__(self):

        #Time of flight sensor
        self.ToFSensor = ()

        #Shooter Motors
        self.Shooter1 = WrapperedSparkMax(constants.SHOOTER_MOTOR1_CANID, "ShooterMotor1")
        self.Shooter2 = WrapperedSparkMax(constants.SHOOTER_MOTOR2_CANID, "ShooterMotor2")

        #Intake Motors
        self.Intake1 = WrapperedSparkMax(constants.INTAKE_MOTOR1_CANID1, "IntakeMotor1")
        self.Intake2 = WrapperedSparkMax(constants.INTAKE_MOTOR2_CANID2, "IntakeMotor2")

        #Floor Roller Motors
        self.FloorRoller1 = WrapperedSparkMax(constants.FlOORROLLER_MOTOR1_CANID, "FloorRollerMotor1")
        self.FloorRoller2 = WrapperedSparkMax(constants.FLOORROLLER_MOTOR2_CANID, "FloorRollerMotor2")

        
        # Calibrations for Shooter (PID Controller)
        self.ShooterkF = Calibration("ShooterkF", 0.00255, "V/RPM")
        self.ShooterkP = Calibration("ShooterkP", 0)

        #Voltage Calibration
        self.IntakeVoltage = Calibration("IntakeVoltage", 12, "V")

    def ActiveShooter(self,desVel): # Desired Velocity
        self.Shooter1.setVelCmd(RPM2RadPerSec(desVel)) # ArbFF default 0
        self.Shooter1.setVelCmd(RPM2RadPerSec(desVel)) # ArbFF defualt 0 

    def ActiveIntake(self): 
        self.Intake1.setVoltage(self.IntakeVoltage)
        self.Intake2.setVoltage(self.IntakeVoltage)

    def ActiveFloorRoller(self):
        self.FloorRoller1.setVoltage(self.IntakeVoltage)
        self.FloorRoller2.setVoltage(self.IntakeVoltage)

    
   

        # SparkMax motor for the floor roller


    def getOperatorControlXboxControl():
        pass




    # What the "note flow control" has to get, which is the xbox control, from the Operator Control node.