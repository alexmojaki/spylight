
CELL_SIZE = 32
RESPAWN_TIME = 2 # in seconds
GAME_DURATION = 3 # in minutes
SPY_TEAM = 1
MERC_TEAM = 0

MAX_SPY_SPEED = 30	# /!\ @WARNING: /!\ This value needs to be smaller than const.CELL_SIZE, else collisions won't work
MAX_MERC_SPEED = 30	# /!\ @WARNING: /!\ This value needs to be smaller than const.CELL_SIZE, else collisions won't work

MAX_SPY_HP = 100
MAX_MERC_HP = 100

MERC_SIGHT_RANGE = 100
SPY_SIGHT_RANGE = 200

SPY_GUN_ANGLE_ERROR = 0.02
SPY_GUN_RANGE  = 100
SPY_GUN_DPS = 30

MERC_GUN_ANGLE_ERROR = 0.02
MERC_GUN_RANGE  = 100
MERC_GUN_DPS = 30