#Priorities
#Finish ToF sensor stuff in init



from wpilib import PWMSparkMax
from utils.calibration import Calibration
from utils import constants, faults
from utils.units import RPM2RadPerSec, m2in
from wrappers.wrapperedSparkMax import WrapperedSparkMax
from playingwithfusion import TimeOfFlight


class gamepieceHandling:
    def __init__(self):
        
        self.hasGamePiece = False
        #Time of flight sensor
        #Finish ToF sensor
        self.ToFSensor = TimeOfFlight(16) #? Don't know what the ID is right now
        self.ToFSensor.setRangingMode(TimeOfFlight.RangingMode.kShort, 24) # 24 is 2023 values
        self.ToFSensor.setRangeOfInterest(6, 6, 10, 10) # fov for sensor (2023 code)
        
        #fault
        self.disconTOFFault = faults.Fault("Shooter TOF Sensor", "Disconnected")

        #Shooter Motors
        self.Shooter1 = WrapperedSparkMax(constants.SHOOTER_MOTOR1_CANID, "ShooterMotor1")
        self.Shooter2 = WrapperedSparkMax(constants.SHOOTER_MOTOR2_CANID, "ShooterMotor2")

        #Intake Motors
        self.Intake1 = WrapperedSparkMax(constants.INTAKE_MOTOR1_CANID1, "IntakeMotor1")
        self.Intake2 = WrapperedSparkMax(constants.INTAKE_MOTOR2_CANID2, "IntakeMotor2")

        #Floor Roller Motors
        self.FloorRoller1 = WrapperedSparkMax(constants.FlOORROLLER_MOTOR1_CANID, "FloorRollerMotor1")
        self.FloorRoller2 = WrapperedSparkMax(constants.FLOORROLLER_MOTOR2_CANID, "FloorRollerMotor2")
        
        # Calibrations for Shooter
        self.ShooterkF = Calibration("ShooterkF", 0.00255, "V/RPM")
        self.ShooterkP = Calibration("ShooterkP", 0)

        #Calibrations for Gamepiece being absent and present
        self.GamePiecePresent = Calibration("Note/Gamepiece", "in", 7) #2023 values 
        self.GamePieceAbsent = Calibration("Note/Gamepiece", "in", 11) #2023 values

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

    def update(self):
        gamepieceDistSensorMeas = m2in(self.ToFSensor.getRange()/1000.0)
        self.disconTOFFault.set(self.ToFSensor.getFirmwareVersion() == 0)


        if (gamepieceDistSensorMeas < self.GamePiecePresent.get()):
            self.hasGamePiece = True
        elif(gamepieceDistSensorMeas > self.GamePieceAbsent.get()):
            self.hasGamePiece = False
        else:
            pass
        

   

        # SparkMax motor for the floor roller


    #def getOperatorControlXboxControl():
     #   pass   




    # What the "note flow control" has to get, which is the xbox control, from the Operator Control node