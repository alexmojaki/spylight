from kivy.lang import Builder
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty, BooleanProperty

from kivy.uix.widget import Widget
from kivy.core.window import Window
# from kivy.graphics import Ellipse, Triangle

from client import utils
from client.environment import KVStringAble, RelativeWidget

Builder.load_string('''
<Character>:
    size: 32,32
    center: root.screenpos

    canvas:
        PushMatrix:
        Translate:
            x: self.x + 16  # +16 to offset the sprite size
            y: self.y + 16
        PushMatrix:
        Rotate:
            angle: self.rotation
        Rectangle:
            pos: -16, -16  # Allows to rotate from the center of the sprite
            size: 32, 32
            source: self.sprite
        PopMatrix:
        PopMatrix:
''')

teams = None


class SpyVision(KVStringAble):
    def __init__(self, char):
        super(SpyVision, self).__init__()
        self.char = char
        d = 200  # diameter
        self.size = 200, 200
        self.pos = (self.char.screenpos[0] - d/2, self.char.screenpos[1] - d/2)
        self.kv_string_template = '''
{indent}Ellipse:
{indent}    pos: {instance}.pos
{indent}    size: {instance}.size
'''


class MercVision(KVStringAble):
    points = ListProperty([])

    def __init__(self, char):
        super(MercVision, self).__init__()
        self.char = char
        self.points = [self.char.screenpos[0], self.char.screenpos[1],
                       self.char.screenpos[0] - 100, self.char.screenpos[1] + 100,
                       self.char.screenpos[0] + 100, self.char.screenpos[1] + 100]
        self.kv_string_template = '''
{indent}Triangle:
{indent}    points: {instance}.points
'''


class Character(Widget):
    offsetx = NumericProperty(0)
    offsety = NumericProperty(0)
    offset = ReferenceListProperty(offsetx, offsety)
    rotation = NumericProperty(0)

    def __init__(self, team, playerid, nick, **kwargs):
        self.team = team
        self.screenpos = Window.size[0]/2, Window.size[1]/2
        self.playerid = playerid
        self.nick = nick
        self.sprite = teams[team]['sprite']
        self.gamepos = (0, 0)
        super(Character, self).__init__(**kwargs)

    def update(self, data):
        self.set_game_pos(data['p'])
        self.rotation = data['d']

    def set_game_pos(self, pos):
        self.gamepos = pos
        self.update_offset()

    def update_offset(self):
        self.offsetx = self.screenpos[0] - self.gamepos[0]
        self.offsety = self.screenpos[1] - self.gamepos[1]

    def get_vision(self):
        return teams[self.team]['vision_class'](self)


class Replica(RelativeWidget, KVStringAble):
    visible = BooleanProperty(False)
    rotation = NumericProperty(0)
    kv_string_template = '''
{indent}PushMatrix:
{indent}Translate:
{indent}    xy: {instance}.pos
{indent}PushMatrix:
{indent}Rotate:
{indent}    angle: {instance}.rotation
{indent}Rectangle:
{indent}    pos: 0, 0
{indent}    size: 32, 32
{indent}    source: {instance}.sprite
{indent}PopMatrix:
{indent}PopMatrix:
'''

    def __init__(self, team, playerid, nick, **kwargs):
        super(Replica, self).__init__(**kwargs)
        self.team = team
        self.playerid = playerid
        self.nick = nick
        self.sprite = teams[team]['sprite']

    def on_visible(self, instance, value):
        if value is False:
            self.static_pos = (-50, -50)

    def update(self, data):  # format: [id, x, y, rotation]
        self.static_pos = (data[1], data[2])
        self.rotation = data[3]


# The order of the entries must be coherent with the value of the team ids in common.game_constants
teams = [
    {'name': 'e mercenaire', 'sprite': utils.spritePath.format('mercenary'), 'vision_class': MercVision},
    {'name': '\'espion', 'sprite': utils.spritePath.format('spy'), 'vision_class': SpyVision}
]
