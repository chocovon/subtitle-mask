import win32api
from pynput import mouse


class MouseMoveMonitor:
    def __init__(self):
        self.x1 = -1
        self.x2 = -1
        self.y1 = -1
        self.y2 = -1

        self.last_x = -2
        self.last_y = -2

        self._on_enter = lambda: None
        self._on_leave = lambda: None

        self._disabled = False

        listener = mouse.Listener(on_move=self._on_move)
        listener.start()

    def disable(self):
        self._disabled = True

    def enable(self):
        self._disabled = False

    def update_region(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def register_on_enter(self, cb):
        self._on_enter = cb

    def register_on_leave(self, cb):
        self._on_leave = cb

    def _on_move(self, _, __):
        if self._disabled:
            return

        cur_pos = win32api.GetCursorPos()
        x = cur_pos[0]
        y = cur_pos[1]

        if self._in_region(x, y):
            if not self._in_region(self.last_x, self.last_y):
                self._on_enter()
        if not self._in_region(x, y):
            if self._in_region(self.last_x, self.last_y):
                self._on_leave()
        self.last_x = x
        self.last_y = y

    def _in_region(self, x, y):
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
