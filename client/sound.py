from kivy.core.audio import SoundLoader
from client import utils
from kivy.logger import Logger


class SoundManager(object):

    def __init__(self):
        self.sounds = {
            'beep': SoundLoader.load(utils.wavPath.format('beep')),
            'shot': SoundLoader.load(utils.wavPath.format('shot')),
            'reload': SoundLoader.load(utils.wavPath.format('reload')),
            'modem': SoundLoader.load(utils.wavPath.format('modem')),
            'punch': SoundLoader.load(utils.wavPath.format('punch')),
            'boom': SoundLoader.load(utils.wavPath.format('boom'))
        }

    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
        else:
            Logger.warn('SL|SoundManager: Sound not found: %s', sound_name)
