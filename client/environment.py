
from kivy.properties import NumericProperty, ObjectProperty, ReferenceListProperty
from kivy.uix.widget import Widget
from kivy.lang import Builder

from client import utils
import common.game_constants as c

Builder.load_file(utils.kvPath.format('environment'))


class RelativeWidget(Widget):
    def __init__(self, **kwargs):
        super(RelativeWidget, self).__init__(**kwargs)
        self.static_pos = kwargs['pos']

    def update_pos(self, parent, value):
        self.x = value[0] + self.static_pos[0]
        self.y = value[1] + self.static_pos[1]


class MapView(RelativeWidget):
    groundTexture = ObjectProperty(None)
    character = ObjectProperty(None)
    shadow = ObjectProperty(None)

    def __init__(self, cellMap, character=None, shadow=None):
        self.character = character
        self.shadow = shadow
        self.groundTexture = utils.getTexture('wall2')
        self.map = cellMap
        super(MapView, self).__init__(size=self.to_pixel(cellMap.size),
                                      pos=(0, 0))

        for x in xrange(cellMap.width):
            for y in xrange(cellMap.height):
                if cellMap.getWallType(x, y) != -1:
                    wall = Wall(pos=self.to_pixel((x, y)))
                    self.add_widget(wall)
                    self.bind(pos=wall.update_pos)
                elif cellMap.getItem(x, y) == 0:
                    item = Terminal(pos=self.to_pixel((x, y)))
                    self.add_widget(item)

    def to_pixel(self, coord):
        return (coord[0] * c.CELL_SIZE,
                coord[1] * c.CELL_SIZE)


class Wall(RelativeWidget):
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
