from kivy.logger import Logger

from client.config import config


class ActionManager(object):
    _ARB_DIR_TO_ANGLE = {
        11: 45,
        10: 0,
        9: 315,
        1: 90,
        0: 0,
        -1: 270,
        -9: 135,
        -10: 180,
        -11: 225
    }

    _ARBITRARY_DIR_VALUES = [10, 1, -10, -1]

    print config.sections()
    _WALK_SPEED = config.get('KeyConfig', 'walkSpeed')

    def __init__(self, networkInterface, keyboardMgr, touchMgr):
        self._ni = networkInterface
        keyboardMgr.bind(movement=self.notify_movement_event)
        keyboardMgr.bind(action=self.notify_action)
        touchMgr.bind(click_state=self.notify_touch_event)

    def notify_action(self, mgr, data):
        pass

    def process_move_angle(self, data):
        pass

    def notify_movement_event(self, keyPressed, keyboardState):
        # Angle calculation @TODO: replace with tangent method?
        s = 0
        for i in xrange(len(self._ARBITRARY_DIR_VALUES)):
            if keyboardState[i]:
                s = s + self._ARBITRARY_DIR_VALUES[i]

        direction = self._ARB_DIR_TO_ANGLE[s]
        speed = 0 if s == 0 else 1 if keyboardState[4] else self._WALK_SPEED
        # Send direction, run state
        print direction, speed
        Logger.debug("SL|Action: direction: %s, speed: %s", direction, speed)
        self._ni.send({'d': direction, 's': speed})

    def notify_touch_event(self, mgr, data):
        pass
