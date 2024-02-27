#this will be in distance along the elevator, with 0 being at bottom and the top being whatever it is
from enum import IntEnum

from wpilib import Timer, TimedRobot
from singerMovement.carriageTelemetry import CarriageTelemetry
from singerMovement.elevatorHeightControl import ElevatorHeightControl
from singerMovement.singerAngleControl import SingerAngleControl
from singerMovement.singerConstants import SINGER_ABS_ENC_OFF_DEG
from utils.singleton import Singleton
from utils.calibration import Calibration
from utils.units import deg2Rad, rad2Deg
from utils.signalLogging import log

# Private enum describing all states in the carriage control state machine
class _CarriageStates(IntEnum):
    LATCH_AT_CURRENT = -1
    HOLD_ALL = 0
    RECALC_TARGETS = 1
    RUN_TO_SAFE_HEIGHT = 2
    ROT_AT_SAFE_HEIGHT = 3
    ROT_ABOVE_SAFE_HEIGHT = 4
    DESCEND_BELOW_SAFE_HEIGHT = 5
    RUN_TO_HEIGHT = 6
    ROTATE_TO_ANGLE = 7

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
        self.singerRotIntake = Calibration(name="Singer Rot Intake", units="deg", default=SINGER_ABS_ENC_OFF_DEG)
        self.singerRotAmp= Calibration(name="Singer Rot Amp", units="deg", default=-40.0 )
        self.singerRotTrap = Calibration(name="Singer Rot Trap", units="deg", default=-20.0 )
        self.singerRotSub = Calibration(name="Singer Sub Shot", units="deg", default=55.0)

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

        self.curElevHeight = 0.5
        self.curSingerAngle = deg2Rad(self.singerCtrl.absEncOffsetDeg)
        self.desElevHeight = 0.5
        self.desSingerAngle = deg2Rad(self.singerCtrl.absEncOffsetDeg)
        self.profiledElevHeight = self.desElevHeight
        self.profiledSingerRot = self.curSingerAngle

        # State machine "from-init" actions
        self._stateMachineInit()

        # Default inputs from the outside world
        self.autoAlignSingerRotCmd = 0.0
        self.curPosCmd = CarriageControlCmd.HOLD

        #Code to disable all elevator & singer movement
        self.DISABLE_SINGER_MOVEMENT = False

        self.telem = CarriageTelemetry()

        self.singerCtrl.setStopped()
        self.elevCtrl.setStopped()
    
    def initFromAbsoluteSensors(self):
        self.elevCtrl.initFromAbsoluteSensor()
        self.singerCtrl.initFromAbsoluteSensor()

    def _stateMachineInit(self):
        self.curState = _CarriageStates.LATCH_AT_CURRENT


    # Use the current position command to calculate
    # The unprofiled elevator height in meters
    def _getUnprofiledElevHeightCmd(self):
        if(self.curPosCmd == CarriageControlCmd.HOLD):
            return self.desElevHeight
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
            return self.desSingerAngle ## This is in rads
        elif(self.curPosCmd == CarriageControlCmd.INTAKE):
            return deg2Rad(self.singerRotIntake.get())
        elif(self.curPosCmd == CarriageControlCmd.AMP):
            return deg2Rad(self.singerRotAmp.get())
        elif(self.curPosCmd == CarriageControlCmd.TRAP):
            return deg2Rad(self.singerRotTrap.get())
        elif(self.curPosCmd == CarriageControlCmd.SUB_SHOT):
            return deg2Rad(self.singerRotSub.get())
        elif(self.curPosCmd == CarriageControlCmd.AUTO_ALIGN):
            return self.curSingerAngle # No motion commanded (already in rads)
        else:
            return 0.0 ## this could be really dangerous depending where we are!
        
    # Should get called in robot code on init to reset internal logic
    def onEnable(self, useFuncGen = False):
        if(useFuncGen):
            self._funcGenInit()
        else:
            self._stateMachineInit()
    
    def manSingerCmd(self,cmdIn):
        self.singerCtrl.manualCtrl(cmdIn)

    # Does a one-time read of all sensors that are needed
    # for carriage control logic
    def _readSensors(self):
        self.curElevHeight = self.elevCtrl.getHeightM()
        self.curSingerAngle = self.singerCtrl.getAngleRad()

    # Should be called in robot code once every 20ms
    def update(self, useFuncGen = False):
        #######################################################
        # Read sensor inputs
        self._readSensors()

        # Run control strategy
        if(useFuncGen):
            self._funcGenUpdate()
        else:
            self._stateMachineUpdate()

        #######################################################
        # Run Motors
        if self.DISABLE_SINGER_MOVEMENT == False:
            self.elevCtrl.update()
            self.singerCtrl.update()

        log("Carriage State", self.curState, "state")
        log("Carriage Cmd", self.curPosCmd, "state")
        self.telem.set(
            self.singerCtrl.getProfiledDesPos(),
            self.curSingerAngle,
            self.elevCtrl.getProfiledDesPos(),
            self.curElevHeight
        )

    # Reset the function generator 
    def _funcGenInit(self):
        self.singerFuncGenStart = self.curSingerAngle 
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

        ################################################################
        # Step 1 - Execute in-state behavior

        if(self.curState == _CarriageStates.LATCH_AT_CURRENT):
            self.elevFinalHeight  = self.curElevHeight + self.elevCtrl.getStoppingDistanceM()
            self.singerFinalAngle = self.curSingerAngle + self.singerCtrl.getStoppingDistanceRad()
            self.desSingerAngle = self.singerFinalAngle
            self.desElevHeight = self.elevFinalHeight

        elif(self.curState == _CarriageStates.HOLD_ALL):
            self.desElevHeight = self.elevFinalHeight

            shouldAutoAlign = (self.curPosCmd == CarriageControlCmd.AUTO_ALIGN)
            if(shouldAutoAlign):
                self.singerFinalAngle = self.autoAlignSingerRotCmd

            self.desSingerAngle = self.singerFinalAngle

        elif(self.curState == _CarriageStates.RECALC_TARGETS):
            self.desElevHeight = self.curElevHeight
            self.desSingerAngle = self.curSingerAngle

            self.elevStartHeight = self.curElevHeight
            self.singerStartAngle = self.curSingerAngle
            self.elevFinalHeight = self._getUnprofiledElevHeightCmd()
            self.singerFinalAngle = self._getUnprofiledSingerRotCmd()

        elif(self.curState == _CarriageStates.RUN_TO_SAFE_HEIGHT):
            self.desElevHeight = self.elevatorMinSafeHeight.get()
            self.desSingerAngle = self.singerStartAngle

        elif(self.curState == _CarriageStates.ROT_ABOVE_SAFE_HEIGHT):
            self.desElevHeight = self.elevStartHeight
            self.desSingerAngle = self.singerFinalAngle

        elif(self.curState == _CarriageStates.ROT_AT_SAFE_HEIGHT):
            self.desElevHeight = self.elevatorMinSafeHeight.get()
            self.desSingerAngle = self.singerFinalAngle

        elif(self.curState == _CarriageStates.DESCEND_BELOW_SAFE_HEIGHT):
            self.desElevHeight = self.elevFinalHeight
            self.desSingerAngle = self.singerFinalAngle

        elif(self.curState == _CarriageStates.RUN_TO_HEIGHT):
            self.desElevHeight = self.elevFinalHeight
            self.desSingerAngle = self.singerStartAngle

        elif(self.curState == _CarriageStates.ROTATE_TO_ANGLE):
            self.desElevHeight = self.elevFinalHeight
            self.desSingerAngle = self.singerFinalAngle

        self.elevCtrl.setDesPos(self.desElevHeight)
        self.singerCtrl.setDesPos(self.desSingerAngle)

        ################################################################
        # Step 2 - Evaluate what the next state is


        if(self.curState == _CarriageStates.LATCH_AT_CURRENT):
            nextState = _CarriageStates.HOLD_ALL

        elif(self.curState == _CarriageStates.HOLD_ALL):
            if(self.curPosCmd != self.prevPosCmd and self.curPosCmd != CarriageControlCmd.HOLD):
                nextState = _CarriageStates.RECALC_TARGETS
            else:
                nextState = _CarriageStates.HOLD_ALL

        elif(self.curState == _CarriageStates.RECALC_TARGETS):
            # New position command is here, let's see how to handle it
            angleErr = abs(
                self.curSingerAngle - self._getUnprofiledSingerRotCmd()
            )
            goingBelowSafe = self._getUnprofiledElevHeightCmd() < self.elevatorMinSafeHeight.get()
            rotateMoreThanThresh = angleErr > deg2Rad(25.0)

            if(goingBelowSafe and rotateMoreThanThresh):
                currentlyBelowSafe = self.elevCtrl.getHeightM() < self.elevatorMinSafeHeight.get()
                if(currentlyBelowSafe):
                    # We need to rotate, we're currently below the safe height,
                    # and we're going to end up below it when we're done.
                    # Command a linear translation up to the safe height first
                    nextState = _CarriageStates.RUN_TO_SAFE_HEIGHT
                else:
                    # We're above safe height but going below it
                    # We can rotate now, but have to rotate first before going down
                    nextState = _CarriageStates.ROT_ABOVE_SAFE_HEIGHT
                    
            else:
                # We can do the normal elevator-then-singer sequence.
                nextState = _CarriageStates.RUN_TO_HEIGHT

        elif(self.curState == _CarriageStates.RUN_TO_SAFE_HEIGHT):
            if(self.elevCtrl.atTarget()):
                # If we're done moving the elevator, move on.
                nextState = _CarriageStates.ROT_AT_SAFE_HEIGHT
            elif(self.curPosCmd == CarriageControlCmd.HOLD):
                # User commanded us to stop moving wherever we were at
                nextState = _CarriageStates.LATCH_AT_CURRENT
            elif(self.curPosCmd != self.prevPosCmd):
                # Command changed, need to recalc targets and start over
                nextState = _CarriageStates.RECALC_TARGETS
            else:
                nextState = _CarriageStates.RUN_TO_SAFE_HEIGHT

        elif(self.curState == _CarriageStates.ROT_ABOVE_SAFE_HEIGHT):
            if(self.singerCtrl.atTarget()):
                # If we're done moving the Singer, move on.
                nextState = _CarriageStates.DESCEND_BELOW_SAFE_HEIGHT
            elif(self.curPosCmd == CarriageControlCmd.HOLD):
                # User commanded us to stop moving wherever we were at
                nextState = _CarriageStates.LATCH_AT_CURRENT
            elif(self.curPosCmd != self.prevPosCmd):
                # Command changed, need to recalc targets and start over
                nextState = _CarriageStates.RECALC_TARGETS
            else:
                nextState = _CarriageStates.ROT_ABOVE_SAFE_HEIGHT

        elif(self.curState == _CarriageStates.ROT_AT_SAFE_HEIGHT):
            if(self.singerCtrl.atTarget()):
                # If we're done moving the Singer, move on.
                nextState = _CarriageStates.DESCEND_BELOW_SAFE_HEIGHT
            elif(self.curPosCmd == CarriageControlCmd.HOLD):
                # User commanded us to stop moving wherever we were at
                nextState = _CarriageStates.LATCH_AT_CURRENT
            elif(self.curPosCmd != self.prevPosCmd):
                # Command changed, need to recalc targets and start over
                nextState = _CarriageStates.RECALC_TARGETS
            else:
                nextState = _CarriageStates.ROT_AT_SAFE_HEIGHT

        elif(self.curState == _CarriageStates.DESCEND_BELOW_SAFE_HEIGHT):
            if(self.elevCtrl.atTarget()):
                # If we're done moving the elevator, move on.
                nextState = _CarriageStates.HOLD_ALL
            elif(self.curPosCmd == CarriageControlCmd.HOLD):
                # User commanded us to stop moving wherever we were at
                nextState = _CarriageStates.LATCH_AT_CURRENT
            elif(self.curPosCmd != self.prevPosCmd):
                # Command changed, need to recalc targets and start over
                nextState = _CarriageStates.RECALC_TARGETS
            else:
                nextState = _CarriageStates.DESCEND_BELOW_SAFE_HEIGHT

        elif(self.curState == _CarriageStates.RUN_TO_HEIGHT):
            if(self.elevCtrl.atTarget()):
                # If we're done moving the elevator, move on.
                nextState = _CarriageStates.ROTATE_TO_ANGLE
            elif(self.curPosCmd == CarriageControlCmd.HOLD):
                # User commanded us to stop moving wherever we were at
                nextState = _CarriageStates.LATCH_AT_CURRENT
            elif(self.curPosCmd != self.prevPosCmd):
                # Command changed, need to recalc targets and start over
                nextState = _CarriageStates.RECALC_TARGETS
            else:
                nextState = _CarriageStates.RUN_TO_HEIGHT

        elif(self.curState == _CarriageStates.ROTATE_TO_ANGLE):
            if(self.singerCtrl.atTarget()):
                # If we're done moving the Singer, move on.
                nextState = _CarriageStates.HOLD_ALL
            elif(self.curPosCmd == CarriageControlCmd.HOLD):
                # User commanded us to stop moving wherever we were at
                nextState = _CarriageStates.LATCH_AT_CURRENT
            elif(self.curPosCmd != self.prevPosCmd):
                # Command changed, need to recalc targets and start over
                nextState = _CarriageStates.RECALC_TARGETS
            else:
                nextState = _CarriageStates.ROTATE_TO_ANGLE

        else:
            nextState = _CarriageStates.HOLD_ALL

        ################################################################
        # Step 3 - Actually transition to the  next state
        self.curState = nextState
        self.prevPosCmd = self.curPosCmd

    # Should be called outside this class whenever anything (driver, automonous, etc) wants to set the target angle for singer auto-align for shot
    def setSignerAutoAlignAngle(self, desiredAngle:float):

        if(self.autoAlignSingerRotCmd > self.singerRotSoftLimitMax.get()):
            self.autoAlignSingerRotCmd = self.singerRotSoftLimitMax.get()

        if(self.autoAlignSingerRotCmd < self.singerRotSoftLimitMin.get()):
            self.autoAlignSingerRotCmd = self.singerRotSoftLimitMin.get()

        self.autoAlignSingerRotCmd = desiredAngle

    # Should be called outside this class whenever anything (driver aoutonomous, etc) wants to change the singer position
    def setPositionCmd(self, curPosCmdIn: CarriageControlCmd):
        self.curPosCmd = curPosCmdIn
        