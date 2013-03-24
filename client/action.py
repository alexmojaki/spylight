from kivy.core.Window import Window

class ActionManager(object):
    def __init__(self, keyboardMgr, networkInterface):
        self._ni = networkInterface

        # Keyboard
        keyboardMgr.bind(up=self.upEvt)
        keyboardMgr.bind(left=self.leftEvt)
        keyboardMgr.bind(down=self.downEvt)
        keyboardMgr.bind(right=self.rightEvt)
        keyboardMgr.bind(run=self.runEvt)
        keyboardMgr.bind(action=self.actionEvt)

        # Mouse/touch
        Window.bind(on_touch_down=self.touch_up)
        Window.bind(on_touch_up=self.touch_down)

    def touch_up(self, event):
        pass

    def touch_down(self, event):
        pass

    def upEvt(self, instance, value):
        pass

    def leftEvt(self, instance, value):
        pass

    def downEvt(self, instance, value):
        pass

    def rightEvt(self, instance, value):
        pass

    def actionEvt(self, instance, value):
        if value:  # keydown only
            pass

    def runEvt(self, instance, value):
        pass

