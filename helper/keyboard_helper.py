import keyboard


# https://stackoverflow.com/a/74247001
class KeyboardHelper:
    def __init__(self):
        self.key_press_cb = None
        self.key_release_cb = None
        keyboard.hook(lambda e: self._on_action(e))

    def register_key_press(self, on_key_press):
        self.key_press_cb = on_key_press

    def register_key_release(self, on_key_release):
        self.key_release_cb = on_key_release

    def _on_action(self, event):
        if event.event_type == keyboard.KEY_DOWN and self.key_press_cb:
            self.key_press_cb(event)

        elif event.event_type == keyboard.KEY_UP and self.key_release_cb:
            self.key_release_cb(event)
