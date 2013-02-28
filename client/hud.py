from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.lang import Builder

from client import utils

class SpylightHUD(Widget):
    def __init__(self, game, gameduration):
        Builder.load_file(utils.kvPath.format('hud'))
        super(SpylightHUD, self).__init__()

        self.timer = Timer(self, gameduration)
        game.add_widget(self.timer)
        self.capInfo = CapInfo()
        game.add_widget(self.capInfo)
        self.game = game

    def start(self):
        Clock.schedule_interval(self.timer.updateTime, 1)
        pass

    def update(self):
        pass


class Timer(Widget):
    time = StringProperty("00:00")


    def __init__(self, hud, gameduration):
        self.minutes = int(gameduration)
        self.seconds = 0
        self.updateTimeString()
        super(Timer, self).__init__()

        self.hud = hud

    def updateTimeString(self):
        self.time = '{0:02d}:{1:02d}'.format(self.minutes, self.seconds)


    def updateTime(self, timeDelta):
        self.seconds -= 1
        if self.seconds == -1:
            self.minutes -= 1
            self.seconds = 59

        self.updateTimeString()

        if self.minutes == 0 and self.seconds == 0:
            self.hud.game.end()


class CapInfo(Widget):
    capFormat = "capture: {0}%"
    percentage = StringProperty('')

    def __init__(self):
        super(CapInfo, self).__init__()
        self.update(0)

    def update(self, newValue):
        self.percentage = CapInfo.capFormat.format(newValue)



