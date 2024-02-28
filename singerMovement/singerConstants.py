#from math import pi
from utils.units import in2m

"""Defines constants that the singer uses"""

#movement that the singer can have if it's being manually controlled by operator
#used in slew rate limiter. All arbitrary numbers
MAX_MAN_ACCEL_MPS2 = in2m(12.0)
MAX_MAN_VEL_MPS = in2m(12.0)
MAX_MANUAL_ROT_ACCEL_DEGPS2 = 20
MAX_MANUAL_DEG_PER_SEC = 30

#movement that the singer can have if it's being controlled by position
MAX_CARRIAGE_VEL_MPS = in2m(24.0)
MAX_CARRIAGE_ACCEL_MPS2 = in2m(24.0)
MAX_SINGER_ROT_VEL_DEG_PER_SEC = 90.0
MAX_SINGER_ROT_ACCEL_DEGPS2 = 90.0

#for operator input to elevator control function in operator interface
ELEVATOR_GEARBOX_GEAR_RATIO = 16.0/1.0
ELEVATOR_SPOOL_RADIUS_M = in2m(0.75)
SINGER_GEARBOX_RATIO = 125.0/1.0

#how fast we want our motor to be running if we are controlling it manually
SINGER_MOTOR_SLOW_FACTOR = .5

SINGER_ABS_ENC_OFF_DEG = 70.0