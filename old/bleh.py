from os.path import join
from kivy.core.image import Image


    # @staticmethod
def getTexture(name, size):
    filename = join('art', name+'.png')
    texture = Image(filename).texture
    texture.wrap = 'repeat'
    texture.uvsize = size
    return texture

class MyTextures(object):

    ground = getTexture(name='ground', size=(32,32))