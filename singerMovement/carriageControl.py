#this will be in distance along the elevator, with 0 being at bottom and the top being whatever it is
from enum import IntEnum

from wpilib import Timer, TimedRobot
from singerMovement.carriageTelemetry import CarriageTelemetry
from singerMovement.elevatorHeightControl import ElevatorHeightControl
from singerMovement.singerAngleControl import SingerAngleControl
from utils.singleton import Singleton
from utils.calibration import Calibration
from utils.units import deg2Rad
from utils.signalLogging import log

# Private enum describing all states in the carriage control state machine
class _CarriageStates(IntEnum):
    HOLD_ALL = 0
    RUN_TO_SAFE_HEIGHT = 1
    ROT_AT_SAFE_HEIGHT = 2
    DESCEND_BELOW_SAFE_HEIGHT = 3
    RUN_TO_HEIGHT = 4
    ROTATE_TO_ANGLE = 5

# All possible positions the carriage can be commanded into
class CarriageControlCmd(IntEnum):
    HOLD = 0
    INTAKE = 1
    AUTO_ALIGN = 2
    AMP = 3
    TRAP = 4
    SUB_SHOT = 5

# Class to control the Carriage (elevator height + singer angle)
# Handles sequencing the two axes to prevent crashing the robot into itself
class CarriageControl(metaclass=Singleton):

    def __init__(self):
        self.elevCtrl = ElevatorHeightControl()
        self.singerCtrl = SingerAngleControl()

        # Fixed Position Cal's
        self.singerRotIntake = Calibration(name="Singer Rot Intake", units="deg", default=70.0 )
        self.singerRotAmp= Calibration(name="Singer Rot Amp", units="deg", default=-40.0 )
        self.singerRotTrap = Calibration(name="Singer Rot Trap", units="deg", default=-20.0 )
        self.singerRotSub = Calibration(name="Singer Sub Shot", units="deg", default =60.0)

        self.elevatorHeightIntake = Calibration(name="Elev Height Intake", units="m", default=0.0 )
        self.elevatorHeightAmp= Calibration(name="Elev Height Amp", units="m", default=0.75 )
        self.elevatorHeightTrap = Calibration(name="Elev Height Trap", units="m", default=0.65 )
        self.elevatorHeightAutoAlign = Calibration(name="Elev Height AutoAlign", units="m", default=0.5 )

        # Physical travel limits
        self.singerRotSoftLimitMax = Calibration(name="Singer Rot Soft Limit Max", units="deg", default= 70.0 )
        self.singerRotSoftLimitMin = Calibration(name="Singer Rot Soft Limit Min", units="deg", default=-20.0 )
        self.elevatorHeightSoftLimitMax = Calibration(name="Elevator Height Soft Limit Max", units="m", default= 0.8 )
        self.elevatorHeightSoftLimitMin = Calibration(name="Elevator Height Soft Limit Min", units="m", default= -0.01)

        # Calibration Function Generator
        self.singerFuncGenAmp = Calibration("Singer Test Function Generator Amp", units="deg", default=0.0)
        self.elevatorFuncGenAmp = Calibration("Elevator Test Function Generator Amp", units="m", default=0.0)
        self.singerFuncGenStart = 0.0
        self.elevFuncGenStart = 0.0
        self.profileStartTime = 0.0
        self.funcGenIsAtStart = True

        # Minimum height that we have to go to before we can freely rotate the singer
        self.elevatorMinSafeHeight = Calibration(name="Elev Min Safe Height", units="m", default=0.4 )

        self.curElevHeight = 0.0
        self.curSingerRot = 0.0
        self.desElevHeight = 0.0
        self.desSingerRot = 0.0
        self.profiledElevHeight = 0.0
        self.profiledSingerRot = 0.0

        self.curPosCmd = CarriageControlCmd.HOLD
        self.prevPosCmd = CarriageControlCmd.HOLD

        self.autoAlignSingerRotCmd = 0.0
        self.useAutoAlignAngleInHold = False

        #Code to disable all elevator & singer movement
        self.disableSingerMovement = False

        # State Machine
        self.curState = _CarriageStates.HOLD_ALL

        self.telem = CarriageTelemetry()

        self.elevatorFuncGenStart = self.curElevHeight
    
    def initFromAbsoluteSensors(self):
        self.elevCtrl.initFromAbsoluteSensor()
        self.singerCtrl.initFromAbsoluteSensor()

    # Use the current position command to calculate
    # The unprofiled elevator height in meters
    def _getUnprofiledElevHeightCmd(self):
        if(self.curPosCmd == CarriageControlCmd.HOLD):
            return self.curElevHeight
        elif(self.curPosCmd == CarriageControlCmd.INTAKE
             or self.curPosCmd == CarriageControlCmd.SUB_SHOT):
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
        elif(self.curPosCmd == CarriageControlCmd.SUB_SHOT):
            return deg2Rad(self.singerRotSub.get())
        elif(self.curPosCmd == CarriageControlCmd.AUTO_ALIGN):
            return self.curSingerRot # No motion commanded
        else:
            return 0.0
        
    def onEnable(self, useFuncGen = False):
        if(useFuncGen):
            self._funcGenStart()
    
    def manSingerCmd(self,cmdIn):
        self.singerCtrl.manualCtrl(cmdIn)

    def update(self, useFuncGen = False):

        #######################################################
        # Read sensor inputs
        self.curElevHeight = self.elevCtrl.getHeightM()
        self.curSingerRot = self.singerCtrl.getAngle()

        # Run control strategy
        if(useFuncGen):
            self._funcGenUpdate()
        else:
            self._stateMachineUpdate()


        #######################################################
        # Run Motors
        if not self.disableSingerMovement:
            self.elevCtrl.update()
            self.singerCtrl.update()

        log("Carriage State", self.curState, "state")
        log("Carriage Cmd", self.curPosCmd, "state")
        
        self.telem.set(
            self.singerCtrl.getProfiledDesPos(),
            self.curSingerRot,
            self.elevCtrl.getProfiledDesPos(),
            self.curElevHeight
        )

    # Reset the function generator 
    def _funcGenStart(self):
        self.singerFuncGenStart = self.curSingerRot 
        self.elevatorFuncGenStart = self.curElevHeight
        self.profileStartTime = Timer.getFPGATimestamp()

    # Update logic to do a periodic function genertor
    def _funcGenUpdate(self):

        if(Timer.getFPGATimestamp() > (self.profileStartTime + 5.0)):
            # Every five seconds, profile to the opposite position
            self.funcGenIsAtStart = not self.funcGenIsAtStart
            self.profileStartTime = Timer.getFPGATimestamp()

        # Get the offsets
        elevOffset = self.elevatorFuncGenAmp.get()
        singerAngleOffset = deg2Rad(self.singerFuncGenAmp.get())

        # Apply the offsets
        if(self.funcGenIsAtStart):
            desPosElevator = self.elevatorFuncGenStart
            desPosSinger = self.singerFuncGenStart
        else:
            desPosElevator = self.elevatorFuncGenStart + elevOffset
            desPosSinger = self.singerFuncGenStart + singerAngleOffset


        # Apply limits to keep from over-extending
        desPosElevator = max(desPosElevator, self.elevatorHeightSoftLimitMin.get())
        desPosElevator = min(desPosElevator, self.elevatorHeightSoftLimitMax.get())
        desPosSinger = max(desPosSinger, self.singerRotSoftLimitMin.get())
        desPosSinger = min(desPosSinger, self.singerRotSoftLimitMax.get())

        self.elevCtrl.setDesPos(desPosElevator)
        self.singerCtrl.setDesPos(desPosSinger)

    # Update logic for the main state machine that makes sure we don't crash into ourselves
    # While going between arbitrary positions
    def _stateMachineUpdate(self):
        # Evaluate in-state behavior
        if(self.curState == _CarriageStates.HOLD_ALL):
            self.elevCtrl.setStopped()
            if(self.useAutoAlignAngleInHold):
                self.singerCtrl.setDesPos(self.autoAlignSingerRotCmd)
            else:
                self.singerCtrl.setDesPos(self.curSingerRot)
        elif(self.curState == _CarriageStates.RUN_TO_SAFE_HEIGHT):
            self.elevCtrl.setDesPos(self.elevatorMinSafeHeight.get())
            self.singerCtrl.setStopped()
        elif(self.curState == _CarriageStates.ROT_AT_SAFE_HEIGHT):
            self.elevCtrl.setStopped()
            self.singerCtrl.setDesPos(self._getUnprofiledSingerRotCmd())
        elif(self.curState == _CarriageStates.DESCEND_BELOW_SAFE_HEIGHT):
            self.elevCtrl.setDesPos(self._getUnprofiledElevHeightCmd())
            self.singerCtrl.setStopped()
        elif(self.curState == _CarriageStates.RUN_TO_HEIGHT):
            self.elevCtrl.setDesPos(self._getUnprofiledElevHeightCmd())
            self.singerCtrl.setStopped()
        elif(self.curState == _CarriageStates.ROTATE_TO_ANGLE):
            self.elevCtrl.setStopped()
            self.singerCtrl.setDesPos(self._getUnprofiledSingerRotCmd())

        # Evalute next state and transition behavior
        nextState = self.curState # Default - stay in the same state
        if(self.curPosCmd == CarriageControlCmd.HOLD):
            nextState = _CarriageStates.HOLD_ALL
        else:
            if(self.curPosCmd != self.prevPosCmd):
                # New position comand is here, let's see how to handle it
                angleErr = abs(
                    self.curSingerRot - self._getUnprofiledSingerRotCmd()
                )
                goingBelowSafe = self._getUnprofiledElevHeightCmd() < self.elevatorMinSafeHeight.get()
                currentlyBelowSafe = self.elevCtrl.getHeightM() < self.elevatorMinSafeHeight.get()
                if(currentlyBelowSafe and goingBelowSafe and angleErr > deg2Rad(3.0)):
                    # We need to rotate, we're currently below the safe height,
                    # and we're going to end up below it when we're done.
                    # Command a linear translation up to the safe height first
                    nextState = _CarriageStates.RUN_TO_SAFE_HEIGHT
                elif(goingBelowSafe and angleErr > deg2Rad(3.0)):
                    # We're above safe height but going below it
                    # We can rotate now, but have to rotate first before going down
                    nextState = _CarriageStates.ROT_AT_SAFE_HEIGHT
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
                        
            if(nextState == _CarriageStates.HOLD_ALL):
                # On all transitions into HOLD_ALL, re-evaluate the auto-alignment command
                self.useAutoAlignAngleInHold = (self.curPosCmd == CarriageControlCmd.AUTO_ALIGN)

        # Finally, actually transition states
        self.curState = nextState

        self.prevPosCmd = self.curPosCmd
        
    # Public API inputs
    def setSignerAutoAlignAngle(self, desiredAngle:float):

        if(self.autoAlignSingerRotCmd > self.singerRotSoftLimitMax.get()):
            self.autoAlignSingerRotCmd = self.singerRotSoftLimitMax.get()

        if(self.autoAlignSingerRotCmd < self.singerRotSoftLimitMin.get()):
            self.autoAlignSingerRotCmd = self.singerRotSoftLimitMin.get()

        self.autoAlignSingerRotCmd = desiredAngle

    def setPositionCmd(self, curPosCmdIn: CarriageControlCmd):
        self.curPosCmd = curPosCmdIn
      