

class ActionManager(object):
    def __init__(self, networkInterface, keyboardMgr, touchMgr):
        self._ni = networkInterface
        keyboardMgr.bind(movement=self.notify_movement_event)
        keyboardMgr.bind(action=self.notify_action)
        touchMgr.bind(click_state=self.notify_touch_event)

    def notify_action(self, mgr, data):
        pass

    def notify_movement_event(self, mgr, data):
        # Angle calculation

        # Send angle, run state
        pass

    def notify_touch_event(self, mgr, data):
        pass
