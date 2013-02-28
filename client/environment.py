
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.lang import Builder

from client import utils
import common.game_constants as c

Builder.load_file(utils.kvPath.format('environment'))

class MapView(Widget):
    width = NumericProperty(0)
    height = NumericProperty(0)
    groundTexture = ObjectProperty(None)
    character = ObjectProperty(None)
    shadow = ObjectProperty(None)
    # impassableTerrain = ListProperty([])

    def __init__(self, cellMap, character, shadow):
        self.character = character
        self.shadow = shadow
        self.groundTexture = utils.getTexture('wall2')
        super(MapView, self).__init__(size=(cellMap.width*c.CELL_SIZE,
                                            cellMap.height*c.CELL_SIZE))

        self.cellMap = cellMap

        for x in xrange(cellMap.width):
            for y in xrange(cellMap.height):
                wall = None
                item = None
                if cellMap.getWallType(x, y) != -1:
                    wall = Wall(pos=(x*c.CELL_SIZE, y*c.CELL_SIZE))
                    self.add_widget(wall)
                    #self.impassableTerrain.append(wall)
                if cellMap.getItem(x,y) == 0:
                    item = Terminal(pos=(x*c.CELL_SIZE, y*c.CELL_SIZE))
                    self.add_widget(item)
                    #self.impassableTerrain.append(item)
                    

class Wall(Widget):
    sprite = utils.spritePath.format('wall')


class Shadow(Widget):
    def __init__(self, sprite, **kwargs):
        self.sprite = sprite
        super(Shadow, self).__init__(**kwargs)



class Terminal(Widget):
    sprite = utils.spritePath.format('terminal')
    pass



class Mine(Widget):
    sprite = utils.spritePath.format('mine')
    def __init__(self, pos, **kwargs):
        self.pos = pos[0]-10, pos[1]-10;
        super(Mine, self).__init__(**kwargs)
