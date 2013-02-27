from kivy.core.image import Image

CELL_SIZE = 32
RESPAWN_TIME = 2 # in seconds
GAME_DURATION = 3 # in minutes
texturePath = 'art/{0}.png'
wavPath = 'art/{0}.wav'

def getTexture(name, size=(CELL_SIZE, CELL_SIZE)):
    filename = texturePath.format(name)
    texture = Image(filename).texture
    texture.wrap = 'repeat'
    texture.uvsize = size
    return texture