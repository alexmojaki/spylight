from kivy.properties import BooleanProperty, NumericProperty, ReferenceListProperty
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.widget import Widget


class KeyboardManager(Widget):
    """
    Dispatches keyboard events.
    They can be binded using: keyboardManager.bind(evt=handler)
    where evt is one of the supported events (up, left, action, quit, etc.)
    and handler is a function taking 2 parameters (3 if there is self too):
        handler(instance, value) or handler(self, instance, value)


    """

    _keyBindings = {
        'up': ['up', 'z'],
        'left': ['left', 'q'],
        'down': ['down', 's'],
        'right': ['right', 'd'],
        'run': ['shift'],  # must be a modifier
        'action': ['e'],
        'quit': ['escape']
    }

    up = BooleanProperty(False)
    left = BooleanProperty(False)
    down = BooleanProperty(False)
    right = BooleanProperty(False)
    run = BooleanProperty(False)
    action = BooleanProperty(False)
    quit = BooleanProperty(False)
    movement = ReferenceListProperty(up, left, down, right, run)

    def __init__(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

    def _keyboard_closed(self):
        Logger.warning('SL|Character: The keyboard is no longer accessible!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Keycode is composed of an integer + a string
        if (keycode[1] in self._keyBindings['up']):
            self.up = True
        if (keycode[1] in self._keyBindings['left']):
            self.left = True
        if (keycode[1] in self._keyBindings['down']):
            self.down = True
        if (keycode[1] in self._keyBindings['right']):
            self.right = True
        if (keycode[1] in self._keyBindings['action']):
            self.action = True
        if (keycode[1] in self._keyBindings['quit']):
            self.quit = True

        if (keycode[1] in self._keyBindings['run'] or
                filter(lambda k: k in self._keyBindings['run'], modifiers)):
            self.run = True

        return True

    def _on_keyboard_up(self, useless, keycode):
        if (keycode[1] in self._keyBindings['up']):
            self.up = False
        if (keycode[1] in self._keyBindings['left']):
            self.left = False
        if (keycode[1] in self._keyBindings['down']):
            self.down = False
        if (keycode[1] in self._keyBindings['right']):
            self.right = False
        if (keycode[1] in self._keyBindings['action']):
            self.action = False
        if (keycode[1] in self._keyBindings['quit']):
            self.quit = False
        if (keycode[1] in self._keyBindings['run']):
            self.run = False

        return True


class TouchManager(Widget):
    mouse_x = NumericProperty(0)
    mouse_y = NumericProperty(0)
    mouse_pos = ReferenceListProperty(mouse_x, mouse_y)
    left_click = BooleanProperty(False)
    click_state = ReferenceListProperty(mouse_pos, left_click)

    def __init__(self):
        Window.bind(on_touch_down=self._on_touch_down)
        Window.bind(on_touch_up=self._on_touch_up)

    def _on_touch_down(self, window, event):
        # event.mouse_pos is not reliable, it sometimes is (0, 0)
        self.mouse_pos = Window.mouse_pos
        if event.button == 'left':
            self.left_click = True

    def _on_touch_up(self, window, event):
        self.mouse_pos = Window.mouse_pos
        if event.button == 'left':
            self.left_click = False
