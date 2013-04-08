from kivy.properties import ListProperty
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.logger import Logger

from client import utils

Builder.load_file(utils.kvPath.format('environment'))


class RelativeWidget(Widget):
    def __init__(self, **kwargs):
        super(RelativeWidget, self).__init__(**kwargs)
        self.static_pos = kwargs['pos']

    def update_pos(self, parent, value):
        self.x = value[0] + self.static_pos[0]
        self.y = value[1] + self.static_pos[1]


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
    kv_string_template = '''
{indent}Triangle:
{indent}    points: {instance}.points
'''

    points = ListProperty([])

    def __init__(self, **kwargs):
        kwargs['kvprefix'] = 'cam_'
        super(Camera, self).__init__(**kwargs)

    def update_pos(self, parent, value):
        super(Camera, self).update_pos(parent, value)
        self.points = [self.x, self.y,
                       self.x - 100, self.y + 100,
                       self.x + 100, self.y + 100]


class Wall(RelativeWidget):
    sprite = utils.spritePath.format('wall')


class Shadow(Widget):
    def __init__(self, sprite, **kwargs):
        self.sprite = sprite
        super(Shadow, self).__init__(**kwargs)


class Terminal(RelativeWidget):
    sprite = utils.spritePath.format('terminal')


class Mine(Widget):
    sprite = utils.spritePath.format('mine')

    def __init__(self, pos, **kwargs):
        self.pos = pos[0]-10, pos[1]-10
        super(Mine, self).__init__(**kwargs)
