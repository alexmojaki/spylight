
from kivy.properties import NumericProperty, ObjectProperty, ReferenceListProperty, ListProperty
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.graphics import Rectangle, Triangle, StencilPush, StencilPop, StencilUse, StencilUnUse
from kivy.logger import Logger

from client import utils
import common.game_constants as c

Builder.load_file(utils.kvPath.format('environment'))

_MAP_VIEW_KV_TEMPLATE = '''
<MapView>:
    size_hint: None, None
    canvas:
        StencilPush
{lightened_areas}
        StencilUse
        Rectangle:
            pos: self.pos
            size: self.size
            texture:self.groundTexture
        StencilUnUse
{lightened_areas}
        StencilPop
'''


class RelativeWidget(Widget):
    def __init__(self, **kwargs):
        super(RelativeWidget, self).__init__(**kwargs)
        self.static_pos = kwargs['pos']

    def update_pos(self, parent, value):
        self.x = value[0] + self.static_pos[0]
        self.y = value[1] + self.static_pos[1]


class LightenedArea(Widget):
    kv_string_template = '''
{indent}Triangle:
{indent}    points: {instance}.points
'''

    def __init__(self, **kwargs):
        super(LightenedArea, self).__init__(**kwargs)

    def kv_string(self, instance='self', indent=8):
        return self.kv_string_template.format(instance=instance, indent=(' ' * indent))


class MapView(RelativeWidget):
    groundTexture = ObjectProperty(None)

    def __init__(self, cellMap, character):
        self.groundTexture = utils.getTexture('wall2')
        self.map = cellMap
        self.char = character
        self.lightened_areas = []
        for cam_pos in cellMap.get_cameras():
            cam = Camera(pos=self.to_pixel(cam_pos))
            self.bind(pos=cam.update_pos)
            self.lightened_areas.append(cam)

        lightened_areas_kvstring = self.la_kv_string()
        print _MAP_VIEW_KV_TEMPLATE.format(lightened_areas=lightened_areas_kvstring)
        Builder.load_string(_MAP_VIEW_KV_TEMPLATE.format(lightened_areas=lightened_areas_kvstring))
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

    def la_kv_string(self):
        output = []
        for i in xrange(len(self.lightened_areas)):
            output.append(self.lightened_areas[i].kv_string('self.lightened_areas[{0}]'.format(i)))
        output.append(self.char.get_vision().kv_string('self.char.get_vision()'))
        return ''.join(output)

    def to_pixel(self, coord):
        return (coord[0] * c.CELL_SIZE,
                coord[1] * c.CELL_SIZE)


class Camera(RelativeWidget, LightenedArea):
    sprite = utils.spritePath.format('camera')
    x = NumericProperty(0)
    y = NumericProperty(0)
    x2 = NumericProperty(0)
    y2 = NumericProperty(0)
    x3 = NumericProperty(0)
    y3 = NumericProperty(0)
    points = ReferenceListProperty(x, y, x2, y2, x3, y3)

    def __init__(self, **kwargs):
        super(Camera, self).__init__(**kwargs)
        # self.pos = kwargs['pos']

    def update_pos(self, parent, value):
        # RelativeWidget.update_pos(self, parent, value)
        super(Camera, self).update_pos(parent, value)
        # print self.pos
        # # self.x = value[0] + self.static_pos[0]
        # # self.y = value[1] + self.static_pos[1]
        self.x2 = self.x - 100
        self.y2 = self.y + 100
        self.x3 = self.x + 100
        self.y3 = self.y + 100
        # Logger.info('SL|Camera: %s', self.points)
        print self.static_pos, self.pos
        # self.points = [self.pos[0], self.pos[1],
        #                self.pos[0] - 100, self.pos[1] + 100,
        #                self.pos[0] + 100, self.pos[1] + 100]
        print self.points

# class Lamp(RelativeWidget):
    # sprite = utils.spritePath.format('camera')


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
        self.pos = pos[0]-10, pos[1]-10
        super(Mine, self).__init__(**kwargs)
