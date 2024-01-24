from utils.units import in2m

"""Defines constants that the singer uses"""

#movement that the singer can have if it's being manually controlled by operator
#used in slew rate limiter. All arbitrary numbers
MAX_MAN_VEL_MPS = in2m(12.0)
MAX_MANUAL_DEG_PER_SEC = 30

#for operator input to elevator control function in operator interface
GEARBOX_GEAR_RATIO = 32
SPROCKET_RADIUS_IN = 1.5 