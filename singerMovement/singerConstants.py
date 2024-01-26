from math import pi
from utils.units import in2m

"""Defines constants that the singer uses"""

#movement that the singer can have if it's being manually controlled by operator
#used in slew rate limiter. All arbitrary numbers
MAX_MAN_VEL_MPS = in2m(12.0)
MAX_MANUAL_DEG_PER_SEC = 30

#for operator input to elevator control function in operator interface
GEARBOX_GEAR_RATIO = 32/1
SPROCKET_RADIUS_M = 1.5 * .0254
#.0254 is the amount of a meter that is one inch. Muliply
SPROCKET_MULTPLICATION_RATIO = SPROCKET_RADIUS_M * 2 * pi

#how fast we want our motor to be running if we are controlling it manually
SINGER_MOTOR_SLOW_FACTOR = .5