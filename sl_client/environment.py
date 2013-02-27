
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.core.image import Image
from kivy.lang import Builder

from custom_logger import logger

import constants as c

Builder.load_file('kv/environment.kv')

class MapView(Widget):
    width = NumericProperty(0)
    height = NumericProperty(0)
    groundTexture = ObjectProperty(None)
    character = ObjectProperty(None)
    shadow = ObjectProperty(None)

    def getTexture(self,name, size):
        filename = c.texturePath.format(name)
        texture = Image(filename).texture
        texture.wrap = 'repeat'
        texture.uvsize = size
        logger.info(filename)
        return texture

    def __init__(self, map, character, shadow):
        self.character = character
        self.shadow = shadow

        super(MapView, self).__init__(size=(map.width*c.CELL_SIZE,
                                            map.height*c.CELL_SIZE))
        self.groundTexture = self.getTexture(name='wall2',
                                             size=(c.CELL_SIZE,c.CELL_SIZE))

        for x in xrange(map.width):
            for y in xrange(map.height):
                if map.getWallType(x, y) != -1:
                    self.add_widget(Wall(pos=(x*c.CELL_SIZE, y*c.CELL_SIZE)))
                if map.getItem(x,y) == 0:
                    self.add_widget(Terminal(pos=(x*c.CELL_SIZE,
                                                  y*c.CELL_SIZE)))


class Wall(Widget):
    pass


class Shadow(Widget):
    def __init__(self, sprite, **kwargs):
        self.sprite = sprite
        super(Shadow, self).__init__(**kwargs)



class Terminal(Widget):
    pass



class Mine(Widget):
    def __init__(self, pos, **kwargs):
        self.pos = pos[0]-10, pos[1]-10;
        super(Mine, self).__init__(**kwargs)
