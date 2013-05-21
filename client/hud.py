# -*- coding: utf-8 -*-

from kivy.uix.widget import Widget
from kivy.properties import StringProperty, NumericProperty
from kivy.lang import Builder
from kivy.uix.anchorlayout import AnchorLayout

from client import utils


class SpylightHUD(Widget):
    def __init__(self, game=None, max_hp=5):
        Builder.load_file(utils.kvPath.format('hud'))
        super(SpylightHUD, self).__init__()
        self.game = game
        self.hp_bar.init(max_hp)

    def update(self, data):
        self.hp_bar.current_hp = data['l'] if data['l'] > 0 else 0
        self.timer.update_time(data['ti'])
        self.cap_info.update(data['pi'])


class Timer(Widget):
    time = StringProperty("00:00")

    def update_time(self, secs):
        self.time = '{0:02d}:{1:02d}'.format(secs // 60, secs % 60)


class CapInfo(Widget):
    capFormat = "Terminal {0}: {1}%"
    percentage = StringProperty('Piratage: N.R.')

    def update(self, status_array):
        if not status_array:
            self.percentage = 'Piratage: N.R.'
        else:
            new_status = []
            for status in status_array:
                new_status.append(self.capFormat.format(*status))
            self.percentage = '\n'.join(new_status)


class EventLog(Widget):
    # text = StringProperty('Il ne se passe rien pour le moment (dans ev)')
    text = StringProperty('')

    def update(self, new_event):
        self.text = 'Evt reçu. TODO détailler format evts'


class HPBar(Widget):
    current_hp = NumericProperty(75)
    max_hp = NumericProperty(100)

    def init(self, max_hp):
        self.max_hp = max_hp
        self.current_hp = max_hp

    def update(self, newValue):
        self.current_hp = newValue


class HUDArea(AnchorLayout):
    pass
