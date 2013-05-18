
CELL_SIZE = 32
RESPAWN_TIME = 2  # in seconds
GAME_DURATION = 3  # in minutes
SPY_TEAM = 1
MERC_TEAM = 0

MAX_SPY_SPEED = 30  # /!\ @WARNING: /!\ This value needs to be smaller than const.CELL_SIZE, else collisions won't work
MAX_MERC_SPEED = 30  # /!\ @WARNING: /!\ This value needs to be smaller than const.CELL_SIZE, else collisions won't work

MAX_SPY_HP = 100
MAX_MERC_HP = 100

MERC_SIGHT_RANGE = 100
SPY_SIGHT_RANGE = 200

SPY_GUN_ANGLE_ERROR = 0.00
SPY_GUN_RANGE = 1000
SPY_GUN_DPS = 30

MERC_GUN_ANGLE_ERROR = 0.00
MERC_GUN_RANGE = 1000
MERC_GUN_DPS = 30

MINE_DPS = 1000  # BOOM!
MINE_BOMB_ACTIVATION_RANGE = 32

ITEMS_TYPE_IDS = {
    "terminal": 10,
    "mine": 20,
    "unkown": 42
}

STEP_STATE_INTERVAL = 1/100.  # 20 times per second
SEND_STATE_INTERVAL = 1/50.  # 10 times per second
