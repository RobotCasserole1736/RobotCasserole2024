


from wpilib import Color8Bit, Mechanism2d
import wpilib

from utils.units import deg2Rad, ft2m, in2m

ROBOT_LEN_M = in2m(29.5) # Length of the Robot
ELEV_MOUNT_HEIGHT_M = in2m(3.0) # Height of base of elevator off of the ground
ELEV_MOUNT_ANGLE_DEG = 60.0 #Angle from Horizon upward for elevator mount
ELEV_MIN_DRAW_DIST = in2m(8.0) # Elevator cannot retract all the way to the bottom - the "zero" point is somewhere up along the angle
SINGER_FWD_DIST = in2m(4.0) # length of the singer forward of the pivot
SINGER_OFFSET_DIST = in2m(4.0) # distance upward from the pivot of the singer
SINGER_REV_DIST = in2m(14.0) # length of the singer behind the pivot

ELEV_COLOR = Color8Bit(200,200,200)
SINGER_COLOR = Color8Bit(255,50,50)

class CarriageTelemetry():
    def __init__(self):
        self.mech = Mechanism2d(in2m(40.0), ft2m(4.0), backgroundColor=Color8Bit(0,0,0))
        self.root = self.mech.getRoot("Root", ROBOT_LEN_M/2.0, ELEV_MOUNT_HEIGHT_M)
        self.elev = self.root.appendLigament("Elevator", self._getElevDrawLen(0.0), ELEV_MOUNT_ANGLE_DEG, 6, ELEV_COLOR)
        self.singerSupport = self.elev.appendLigament("SingerSupport", SINGER_OFFSET_DIST, 0.0, 6, SINGER_COLOR)
        self.singerFwd = self.elev.appendLigament("SingerFwd", SINGER_FWD_DIST, 90.0, 8, SINGER_COLOR)
        self.singerRev = self.elev.appendLigament("SingerRev", SINGER_REV_DIST, -90.0, 8, SINGER_COLOR)
        wpilib.SmartDashboard.putData("Carriage", self.mech)

    def _getElevDrawLen(self, len_in):
        return len_in + ELEV_MIN_DRAW_DIST
    
    def _getSingerSupportDrawAngle(self, angle_in):
        return angle_in - ELEV_MOUNT_ANGLE_DEG

    def set(self, desSingerAngle, actSingerAngle, desElevHeight, actElevHeight):
        self.elev.setLength(self._getElevDrawLen(desElevHeight))
        self.singerSupport.setAngle(self._getSingerSupportDrawAngle(desSingerAngle))