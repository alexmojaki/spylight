import math

from kivy.logger import Logger

from client.config import config
from client.network import MessageFactory
from kivy.core.window import Window


class ActionManager(object):
    _WALK_SPEED = float(config.get('KeyConfig', 'walkSpeed'))
    def __init__(self, networkInterface, keyboardMgr, touchMgr, game):
        self._ni = networkInterface
        self.game = game
        ActionManager.s = self
        keyboardMgr.bind(movement=self.notify_movement_event)
        keyboardMgr.bind(action=self.notify_action)
        touchMgr.bind(click_state=ActionManager.notify_touch_event)

    def notify_action(self, mgr, data):
        if data:
            self._ni.send(MessageFactory.action(True))

    def notify_movement_event(self, keyPressed, keyboardState):
        # Angle calculation @TODO: replace with tangent method?
        dir_to_angle = {
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

        dir_values = [10, 1, -10, -1]
        s = 0
        for i in xrange(len(dir_values)):
            if keyboardState[i]:
                s = s + dir_values[i]

        direction = dir_to_angle[s]
        speed = 0 if s == 0 else 1 if keyboardState[4] else self._WALK_SPEED

        # Send direction, run state
        Logger.debug("SL|Action: direction: %s, speed: %s", direction, speed)
        Logger.debug("SL|Action: Vars types=%s, %s, %s", type(direction), type(speed), type(self._WALK_SPEED))
        self._ni.send(MessageFactory.move(direction, speed))

    @staticmethod
    def notify_touch_event(mgr, data):  # data is [[x,y], bool_down]
        print "Blorg"
        if data[1]:  # on mouse down only
            ActionManager.s._ni.send(MessageFactory.shoot(ActionManager.s._get_angle_with_char(data[0])))

    def _get_angle_with_char(self, other_point):
        cur_pos = self.game.char.gamepos
        # on_screen_pos - offset = in game pos
        dx = other_point[0] - self.game.char.offsetx - cur_pos[0]
        dy = other_point[1] - self.game.char.offsety - cur_pos[1]
        # atan2 returns an angle between -pi and +pi (-180 and + 180)
        return math.degrees(math.atan2(dx, -dy)) + 180  # now 0 - 360

    def notify_orientation(self):
        self._ni.send(MessageFactory.turn(
            self._get_angle_with_char(Window.mouse_pos)))
