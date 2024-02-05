#this will be in distance along the elevator, with 0 being at bottom and the top being whatever it is
from enum import Enum
from singerMovement.elevatorHeightControl import ElevatorHeightControl
from singerMovement.singerAngleControl import SingerAngleControl
from utils.singleton import Singleton
from utils.calibration import Calibration
from utils.units import deg2Rad

class _CarriageStates(Enum):
    HOLD_ALL = 0
    RUN_TO_SAFE_HEIGHT = 1
    ROT_AT_SAFE_HEIGHT = 2
    DESCEND_BELOW_SAFE_HEIGHT = 3
    RUN_TO_HEIGHT = 4
    ROTATE_TO_ANGLE = 5


class CarriageControlCmd(Enum):
    HOLD = 0
    INTAKE = 1
    AUTO_ALIGN = 2
    AMP = 3
    TRAP = 4

class CarriageControl(metaclass=Singleton):

    def __init__(self):
        self.elevCtrl = ElevatorHeightControl()
        self.singerCtrl = SingerAngleControl()

        # Fixed Position Cal's
        self.singerRotIntake = Calibration(name="Singer Rot Intake", units="deg", default=60.0 )
        self.singerRotAmp= Calibration(name="Singer Rot Amp", units="deg", default=-20.0 )
        self.singerRotTrap = Calibration(name="Singer Rot Trap", units="deg", default=-20.0 )

        self.elevatorHeightIntake = Calibration(name="Elev Height Intake", units="m", default=0.0 )
        self.elevatorHeightAmp= Calibration(name="Elev Height Amp", units="m", default=0.75 )
        self.elevatorHeightTrap = Calibration(name="Elev Height Trap", units="m", default=0.75 )
        self.elevatorHeightAutoAlign = Calibration(name="Elev Height AutoAlign", units="m", default=0.5 )

        # Minimum height that we have to go to before we can freely rotate the singer
        self.elevatorMinSafeHeight = Calibration(name="Elev Min Safe Height", units="m", default=0.65 )

        self.curElevHeight = 0.0
        self.curSingerRot = 0.0
        self.desElevHeight = 0.0
        self.desSingerRot = 0.0
        self.profiledElevHeight = 0.0
        self.profiledSingerRot = 0.0

        self.curPosCmd = CarriageControlCmd.HOLD
        self.prevPosCmd = CarriageControlCmd.HOLD

        # State Machine
        self.curState = _CarriageStates.HOLD_ALL
    
    def initFromAbsoluteSensors(self):
        self.elevCtrl.initFromAbsoluteSensor()
        self.singerCtrl.initFromAbsoluteSensor()

    # Use the current position command to calculate
    # The unprofiled elevator height in meters
    def _getUnprofiledElevHeightCmd(self):
        if(self.curPosCmd == CarriageControlCmd.HOLD):
            return self.curElevHeight
        elif(self.curPosCmd == CarriageControlCmd.INTAKE):
            return self.elevatorHeightIntake.get()
        elif(self.curPosCmd == CarriageControlCmd.AMP):
            return self.elevatorHeightAmp.get()
        elif(self.curPosCmd == CarriageControlCmd.TRAP):
            return self.elevatorHeightTrap.get()
        elif(self.curPosCmd == CarriageControlCmd.AUTO_ALIGN):
            return self.elevatorHeightAutoAlign.get()
        else:
            return 0.0

    # Use the current position command to calculate
    # The unprofiled elevator height in radians
    def _getUnprofiledSingerRotCmd(self):
        if(self.curPosCmd == CarriageControlCmd.HOLD):
            return self.curSingerRot
        elif(self.curPosCmd == CarriageControlCmd.INTAKE):
            return deg2Rad(self.singerRotIntake.get())
        elif(self.curPosCmd == CarriageControlCmd.AMP):
            return deg2Rad(self.singerRotAmp.get())
        elif(self.curPosCmd == CarriageControlCmd.TRAP):
            return deg2Rad(self.singerRotTrap.get())
        elif(self.curPosCmd == CarriageControlCmd.AUTO_ALIGN):
            return self.autoAlignSingerRotCmd 
        else:
            return 0.0

    

    def update(self):

        #######################################################
        # Read sensor inputs

        self.curElevHeight = self.elevCtrl.getHeightM()
        self.curSingerRot = self.singerCtrl.getAngle()
 
        #######################################################
        # Run the state machine


        # Evaluate in-state behavior
        if(self.curState == _CarriageStates.HOLD_ALL):
            # hold - current = actual
            self.desElevHeight = self.profiledElevHeight = self.curElevHeight
            self.desSingerRot = self.profiledSingerRot = self.curSingerRot
        elif(self.curState == _CarriageStates.RUN_TO_SAFE_HEIGHT):
            pass
        elif(self.curState == _CarriageStates.ROT_AT_SAFE_HEIGHT):
            pass
        elif(self.curState == _CarriageStates.DESCEND_BELOW_SAFE_HEIGHT):
            pass
        elif(self.curState == _CarriageStates.RUN_TO_HEIGHT):
            pass
        elif(self.curState == _CarriageStates.ROTATE_TO_ANGLE):
            pass

        # Evalute next state and transition behavior
        nextState = self.curState # Default - stay in the same state
        if(self.curState == _CarriageStates.HOLD_ALL):
            if(self.curPosCmd != self.prevPosCmd):
                # New position comand is here, let's see how to handle it
                angleErr = abs(
                    self.curSingerRot - self._getUnprofiledSingerRotCmd()
                )
                belowSafe = self._getUnprofiledElevHeightCmd() > self.elevatorMinSafeHeight.get()
                if(belowSafe and angleErr > deg2Rad(10.0)):
                    # We need to go below the safe height and we need to rotate. 
                    # We have to go up to the safe height first.
                    nextState = _CarriageStates.RUN_TO_SAFE_HEIGHT
                else:
                    # We can do the normal elevator-then-singer sequence.
                    nextState = _CarriageStates.RUN_TO_HEIGHT

        elif(self.curState == _CarriageStates.RUN_TO_SAFE_HEIGHT):
            if(self.elevCtrl.atTarget()):
                # If we're done moving the elevator, move on.
                nextState = _CarriageStates.ROT_AT_SAFE_HEIGHT

        elif(self.curState == _CarriageStates.ROT_AT_SAFE_HEIGHT):
            if(self.singerCtrl.atTarget()):
                # If we're done rotating the singer, move on.
                nextState = _CarriageStates.DESCEND_BELOW_SAFE_HEIGHT

        elif(self.curState == _CarriageStates.DESCEND_BELOW_SAFE_HEIGHT):
            if(self.elevCtrl.atTarget()):
                # If we'relowering down, we're done
                nextState = _CarriageStates.HOLD_ALL

        elif(self.curState == _CarriageStates.RUN_TO_HEIGHT):
            if(self.elevCtrl.atTarget()):
                # If we're done moving the elevator, move on.
                nextState = _CarriageStates.ROT_AT_SAFE_HEIGHT
                
        elif(self.curState == _CarriageStates.ROTATE_TO_ANGLE):
           if(self.singerCtrl.atTarget()):
                # If we're done rotating the singer, we're done
                nextState = _CarriageStates.HOLD_ALL


        # Finally, actually transition states
        self.curState = nextState

    #will need to get command position from the operator controller and
    #desired singer angle for autolign"""

    def setSignerAutoAlignAngle(self, desiredAngle:float):
        self.autoAlignSingerRotCmd = desiredAngle
    
    def setPositionCmd(self, curPosCmdIn: CarriageControlCmd):
        self.curPosCmd = curPosCmdIn