from kivy.properties import ListProperty
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.clock import Clock

from client import utils
from common import game_constants as const
Builder.load_file(utils.kvPath.format('environment'))


class RelativeWidget(Widget):
    def __init__(self, **kwargs):
        super(RelativeWidget, self).__init__(**kwargs)
        self.static_pos = kwargs['pos']

    def update_pos(self, parent, value):
        self.pos = [value[0] + self.static_pos[0],
                    value[1] + self.static_pos[1]]


# class LightenedArea(Widget):
#     # Example string template
#     kv_string_template = '''
# {indent}Rectangle:
# {indent}    pos: 100, 100
# {indent}    size: 32, 32
# '''

#     def __init__(self, **kwargs):
#         super(LightenedArea, self).__init__(**kwargs)

#     def kv_string(self, instance='self', indent=8):
#         return self.kv_string_template.format(instance=instance,
#                                               indent=(' ' * indent))


class KVStringAble(Widget):
    kvid = 0  # Used to generate a unique id.
    kv_string_template = '''
{indent}{instance}
'''

    def __init__(self, kvprefix='obj_', **kwargs):
        super(KVStringAble, self).__init__(**kwargs)
        self.kvname = kvprefix + str(KVStringAble.kvid)
        KVStringAble.kvid = KVStringAble.kvid + 1

    def kv_string(self, instance='self', indent=8):
        return self.kv_string_template.format(instance=instance,
                                              indent=(' ' * indent))


class Camera(RelativeWidget, KVStringAble):
    sprite = utils.spritePath.format('camera')
    points = ListProperty([])
    kv_string_template = '''
{indent}Triangle:
{indent}    points: {instance}.points
'''

    def __init__(self, **kwargs):
        sprite_offset = 5  # 32/2 - 11
        x, y = kwargs['pos']
        kwargs['pos'] = (x+sprite_offset, y+sprite_offset)
        kwargs['kvprefix'] = 'cam_'
        self.rotation = kwargs['dir']
        print kwargs['pos']

        # Extra offset to stick to the wall
        # self.pos_offset_x = math.cos(self.rotation)
        # if self.pos_offset_x != 0:
        #     self.pos_offset_x = math.copysign(11, self.pos_offset_x)
        # self.pos_offset_y = math.sin(self.rotation)
        # if self.pos_offset_y != 0:
        #     self.pos_offset_y = math.copysign(11, self.pos_offset_y)
        super(Camera, self).__init__(**kwargs)

    def update_pos(self, parent, value):
        super(Camera, self).update_pos(parent, value)
        self.points = [self.x, self.y,
                       self.x - 100, self.y + 100,
                       self.x + 100, self.y + 100]


class Wall(RelativeWidget, KVStringAble):
    sprite = utils.spritePath.format('wall')
    texture = utils.getTexture('wall')
    SECTION_SIZE = (const.CELL_SIZE, const.CELL_SIZE)
    kv_string_template = '''
{indent}Rectangle:
{indent}    pos: {instance}.pos
{indent}    size: {instance}.size
{indent}    texture: {instance}.texture
{indent}    tex_coords: {instance}.tex_coords
'''

    def kv_string(self, instance='self', indent=8):
        # Fix the texture scaling.
        nb_repeat_x = self.size[0] / self.SECTION_SIZE[0]
        nb_repeat_y = self.size[1] / self.SECTION_SIZE[1]
        self.tex_coords = (
            0, 0,
            nb_repeat_x, 0,
            nb_repeat_x, -nb_repeat_y,
            0, -nb_repeat_y
        )
        return super(Wall, self).kv_string(instance, indent)


class HorizWall(Wall):
    def __init__(self, type, **kwargs):
        self.type = type
        self.size = self.SECTION_SIZE
        super(HorizWall, self).__init__(**kwargs)

    def add_section(self, x, y):
        if y != self.y:
            raise AttributeError('the y must be the same to be in this wall')
        elif x <= self.x:
            raise AttributeError('the wall must be built from left to right')
        else:
            print 'before', self.size
            self.size = (self.size[0] + self.SECTION_SIZE[0], self.size[1])
            print 'after', self.size
        print self.pos, x, y, self.size


class VertWall(Wall):
    def __init__(self, type, **kwargs):
        self.type = type
        self.size = self.SECTION_SIZE
        super(VertWall, self).__init__(**kwargs)

    def add_section(self, x, y):
        if x != self.x:
            raise AttributeError('the y must be the same to be in this wall')
        elif y <= self.y:
            raise AttributeError('the wall must be built from top to bottom')
        else:
            print 'before', self.size
            self.size = (self.size[0], self.size[1] + self.SECTION_SIZE[1])
            self.y -= self.SECTION_SIZE[1]
            print 'after', self.size
        print self.pos, x, y, self.size


class BlockWall(Wall):
    def __init__(self, type, **kwargs):
        self.type = type
        self.size = self.SECTION_SIZE
        super(BlockWall, self).__init__(**kwargs)

    def add_section(self, x, y):
        raise AttributeError('Block walls can\'t be expanded.')


class Terminal(RelativeWidget, KVStringAble):
    sprite = utils.spritePath.format('terminal')
    kv_string_template = '''
{indent}Rectangle:
{indent}    pos: {instance}.pos[0] + 8, {instance}.pos[1] + 8
{indent}    size: 16, 16
{indent}    source: {instance}.sprite
'''


class Mine(Widget):
    sprite = utils.spritePath.format('mine')

    def __init__(self, pos, **kwargs):
        self.pos = pos[0]-10, pos[1]-10
        super(Mine, self).__init__(**kwargs)


class Shot(Widget):
    points = ListProperty([])

    def __init__(self, origin, target, parent, **kwargs):
        self.points = [origin[0], origin[1], target[0], target[1]]
        self._parent = parent  # Care! self.parent is used by Kivy
        super(Shot, self).__init__(**kwargs)
        parent.add_widget(self)
        Clock.schedule_once(self.remove_shot_callback, 0.5)
        # TODO: use schedule interval to make it move?

    def remove_shot_callback(self, dt):
        self._parent.remove_widget(self)
