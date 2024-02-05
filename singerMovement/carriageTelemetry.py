


from wpilib import Color8Bit, Mechanism2d
import wpilib

from utils.units import deg2Rad, ft2m, in2m, rad2Deg

ROBOT_LEN_M = in2m(29.5) # Length of the Robot
ELEV_MOUNT_HEIGHT_M = in2m(3.0) # Height of base of elevator off of the ground
ELEV_MOUNT_ANGLE_DEG = 60.0 #Angle from Horizon upward for elevator mount
ELEV_MIN_DRAW_DIST = in2m(8.0) # Elevator cannot retract all the way to the bottom - the "zero" point is somewhere up along the angle
SINGER_FWD_DIST = in2m(4.0) # length of the singer forward of the pivot
SINGER_OFFSET_DIST = in2m(4.0) # distance upward from the pivot of the singer
SINGER_REV_DIST = in2m(14.0) # length of the singer behind the pivot

ELEV_COLOR = Color8Bit(255,255,255)
SINGER_COLOR = Color8Bit(255,50,50)
GHOST_COLOR = Color8Bit(180,180,180)

# Private class for drawing one elevator and singer on a Mechanism2d
class _ElevatorMech():

    def _getElevDrawLen(self, len_in):
        return len_in + ELEV_MIN_DRAW_DIST
    
    def _getSingerSupportDrawAngle(self, angle_in):
        return angle_in - ELEV_MOUNT_ANGLE_DEG + 90.0

    def __init__(self, root, isDesired):

        size = 3 if isDesired else 6

        ec = GHOST_COLOR if isDesired else ELEV_COLOR
        sc = GHOST_COLOR if isDesired else SINGER_COLOR
        suffix = "_des" if isDesired else "_act"

        self.elev = root.appendLigament(f"Elevator{suffix}", self._getElevDrawLen(0.0), ELEV_MOUNT_ANGLE_DEG, size, ec)
        self.singerSupport = self.elev.appendLigament(f"SingerSupport{suffix}", SINGER_OFFSET_DIST, 0.0, size, sc)
        self.singerFwd = self.singerSupport.appendLigament(f"SingerFwd{suffix}", SINGER_FWD_DIST, -90.0, size, sc)
        self.singerRev = self.singerSupport.appendLigament(f"SingerRev{suffix}", SINGER_REV_DIST, 90.0, size, sc)

    def set(self, singerAngle, elevHeight):
        self.elev.setLength(self._getElevDrawLen(elevHeight))
        self.singerSupport.setAngle(self._getSingerSupportDrawAngle(rad2Deg(singerAngle)))

# Telemetry draws an actual (normal color) and desired (grey ghost) carraige
class CarriageTelemetry():
    def __init__(self):
        self.mech = Mechanism2d(in2m(40.0), ft2m(4.0), backgroundColor=Color8Bit(0,0,0))
        self.root = self.mech.getRoot("Root", ROBOT_LEN_M/2.0, ELEV_MOUNT_HEIGHT_M)
        self.act = _ElevatorMech(self.root, False)
        self.des = _ElevatorMech(self.root, True)
        wpilib.SmartDashboard.putData("Carriage", self.mech)
    

    def set(self, desSingerAngle, actSingerAngle, desElevHeight, actElevHeight):
        self.des.set(desSingerAngle, desElevHeight)
        self.act.set(actSingerAngle, actElevHeight)