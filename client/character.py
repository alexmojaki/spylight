from kivy.lang import Builder
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty, BooleanProperty

from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import Ellipse, Triangle

from client import utils
from client.environment import LightenedArea

Builder.load_string('''
<Character>:
    size: 32,32
    rotation: 0
    center: root.screenpos
    # collisionBox: collisionBox

    Scatter:
        id:scatter
        do_translation: False, False
        do_rotation: False
        do_scale: False
        # size: root.size  # Don't use size! use scale instead (cf Scatter's doc)
        center: root.center
        rotation: root.rotation
        scale: 1.68  # 32/19

        Image:
            source: root.sprite
''')

teams = None


class SpyVision(LightenedArea):
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


class MercVision(LightenedArea):
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

    def __init__(self, team, playerid, nick):
        self.team = team
        self.screenpos = Window.size[0]/2, Window.size[1]/2
        self.center = self.screenpos
        self.playerid = playerid
        self.nick = nick
        self.sprite = teams[team]['sprite']
        self.gamepos = (0, 0)
        super(Character, self).__init__()

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


class Replica(Character):
    visible = BooleanProperty(False)

    def update(self, data):
        pass


MERC_TEAM_ID = 0
SPY_TEAM_ID = 1

teams = [
    {'name': 'e mercenaire', 'sprite': utils.spritePath.format('mercenary'), 'vision_class': MercVision},
    {'name': '\'espion', 'sprite': utils.spritePath.format('spy'), 'vision_class': SpyVision}
]
