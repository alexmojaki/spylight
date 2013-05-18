from kivy.core.image import Image
from common.game_constants import CELL_SIZE


RESPAWN_TIME = 2  # in seconds
GAME_DURATION = 3  # in minutes
spritePath = 'client/art/{0}.png'
wavPath = 'client/art/{0}.wav'
kvPath = 'client/kv/{0}.kv'


def getTexture(name, size=(CELL_SIZE, CELL_SIZE)):
    filename = spritePath.format(name)
    texture = Image(filename).texture
    texture.wrap = 'repeat'
    texture.uvsize = size
    return texture
