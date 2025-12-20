import tkinter as tk
from tkinter import ttk


from helper.blur_helper import blur_top_level
from helper.keyboard_helper import KeyboardHelper
from helper.local_config import LocalConfig
from helper.mouse_move_monitor import MouseMoveMonitor

MODIFIER_KEYS = ['ctrl', 'shift', 'alt', 'cmd', 'win']


class FloatingWindow:
    def __init__(self, master):
        self.master = master
        self.top_level = top_level = tk.Toplevel(master)
        self.showing = True
        self.config = LocalConfig()

        self.hold_to_hide_hotkey = self.config.window_data.hotkeys['hold_to_hide']
        self.toggle_hotkey = self.config.window_data.hotkeys['toggle']
        self.hotkey_to_set = None
        self.active_hotkey_btn = None
        self.original_btn_text = None

        self.default_color = self.top_level.cget('background')
        self.mouse_move_monitor = MouseMoveMonitor()
        self.mouse_move_monitor.register_on_enter(self.show_hints)
        self.mouse_move_monitor.register_on_leave(self.hide_hints)
        self.update_mouse_monitor_region()

        top_level.wm_attributes("-topmost", 1)
        top_level.overrideredirect(True)

        top_level.wm_geometry(self.config.get_geo_str())

        top_level.minsize(100, 30)

        top_level.bind('<B1-Motion>', self.dragging)
        top_level.bind('<Button-1>', self.on_mouse_down)
        top_level.bind("<ButtonRelease-1>", self.on_mouse_release)
        keyboard_helper = KeyboardHelper()
        keyboard_helper.register_key_press(self.on_key_press)
        keyboard_helper.register_key_release(self.on_key_release)

        self.grip = ttk.Sizegrip(self.top_level)

        self.lastClickX = 0
        self.lastClickY = 0

        self.close_button = tk.Button(top_level, text="×", command=self.terminate, borderwidth=0)

        self.hint_frame = tk.Frame(top_level)
        tk.Label(self.hint_frame, text="Hold").pack(side='left')
        self.hold_key_btn = tk.Button(self.hint_frame, text=f"[{self.hold_to_hide_hotkey}]",
                                      command=lambda: self.start_hotkey_setup('hold_to_hide'), borderwidth=0,
                                      cursor="hand2")
        self.hold_key_btn.pack(side='left')
        tk.Label(self.hint_frame, text="or press").pack(side='left')
        self.toggle_key_btn = tk.Button(self.hint_frame, text=f"[{self.toggle_hotkey}]",
                                        command=lambda: self.start_hotkey_setup('toggle'), borderwidth=0,
                                        cursor="hand2")
        self.toggle_key_btn.pack(side='left')
        tk.Label(self.hint_frame, text="to hide / show.").pack(side='left')

        self.need_blur_cb_var = tk.BooleanVar(value=self.config.window_data.need_blur)
        self.need_blur_cb = tk.Checkbutton(top_level, text="Blur mask",
                                           variable=self.need_blur_cb_var,
                                           command=self.on_need_blur_changed)

        if self.config.first_open:
            self.show_hints(init=True)
        else:
            self.blur()

        self.top_level.after(300, self.refresh_topmost)

    def dragging(self, event):
        top_level = self.top_level
        x = event.x - self.lastClickX + top_level.winfo_x()
        y = event.y - self.lastClickY + top_level.winfo_y()
        top_level.geometry("+%s+%s" % (x, y))

    def on_mouse_down(self, event):
        if self.hotkey_to_set:
            self.cancel_hotkey_setup()
        self.lastClickX = event.x
        self.lastClickY = event.y
        self.mouse_move_monitor.disable()

    def toggle(self):
        if self.showing:
            self.hide()
        else:
            self.show()

    def show(self):
        if not self.showing:
            self.top_level.attributes('-alpha', 1)
            self.showing = True

    def hide(self):
        if self.showing:
            self.top_level.attributes('-alpha', 0)
            self.showing = False

    def _is_hotkey_pressed(self, event_name, hotkey_name):
        if hotkey_name in MODIFIER_KEYS:
            return hotkey_name in event_name
        return event_name == hotkey_name

    def on_key_press(self, e):
        if self.hotkey_to_set:
            self.set_hotkey(e)
            return

        if self._is_hotkey_pressed(e.name, self.toggle_hotkey):
            self.toggle()
        if self._is_hotkey_pressed(e.name, self.hold_to_hide_hotkey):
            self.hide()

    def on_key_release(self, e):
        if self._is_hotkey_pressed(e.name, self.hold_to_hide_hotkey):
            self.show()

    def on_mouse_release(self, _):
        geo_obj = {'x': self.top_level.winfo_x(),
                   'y': self.top_level.winfo_y(),
                   'width': self.top_level.winfo_width(),
                   'height': self.top_level.winfo_height()}
        self.config.save_geo(geo_obj)
        self.update_mouse_monitor_region()
        self.mouse_move_monitor.enable()

    def on_need_blur_changed(self):
        self.config.save_need_blur(self.need_blur_cb_var.get())

    def start_hotkey_setup(self, hotkey_type):
        # Cancel if already setting another key, restore its text
        if self.hotkey_to_set:
            self.cancel_hotkey_setup()

        self.hotkey_to_set = hotkey_type
        if hotkey_type == 'hold_to_hide':
            self.active_hotkey_btn = self.hold_key_btn
            self.original_btn_text = f"[{self.hold_to_hide_hotkey}]"
        else:  # 'toggle'
            self.active_hotkey_btn = self.toggle_key_btn
            self.original_btn_text = f"[{self.toggle_hotkey}]"

        self.active_hotkey_btn.config(text="Press a key...")

    def cancel_hotkey_setup(self):
        if not self.hotkey_to_set:
            return

        self.active_hotkey_btn.config(text=self.original_btn_text)
        self.hotkey_to_set = None
        self.active_hotkey_btn = None
        self.original_btn_text = None

    def set_hotkey(self, event):
        key_name = event.name
        hotkey_type = self.hotkey_to_set

        if key_name == 'esc':
            self.cancel_hotkey_setup()
            return

        # Normalize modifier keys
        for mod in MODIFIER_KEYS:
            if mod in key_name:
                key_name = mod
                break

        # Check for conflicts
        if (hotkey_type == 'hold_to_hide' and key_name == self.toggle_hotkey) or \
           (hotkey_type == 'toggle' and key_name == self.hold_to_hide_hotkey):
            self.cancel_hotkey_setup()
            return

        if hotkey_type == 'hold_to_hide':
            self.hold_to_hide_hotkey = key_name
        else:  # 'toggle'
            self.toggle_hotkey = key_name

        self.config.save_hotkey(hotkey_type, key_name)
        self.active_hotkey_btn.config(text=f"[{key_name}]")
        self.hotkey_to_set = None

    def terminate(self):
        self.master.quit()
        quit()

    def update_mouse_monitor_region(self):
        wd = self.config.window_data
        x = wd.x
        y = wd.y
        width = wd.width
        height = wd.height
        self.mouse_move_monitor.update_region(x, x + width, y, y + height)

    def show_hints(self, init=False):
        self.close_button.pack(side="top", anchor="ne")
        self.grip.pack(side="bottom", anchor="se")
        self.hint_frame.pack(anchor="center")
        self.need_blur_cb.pack(anchor="center")
        if not init:
            self.no_blur()

    def hide_hints(self):
        self.close_button.pack_forget()
        self.grip.pack_forget()
        self.hint_frame.pack_forget()
        self.need_blur_cb.pack_forget()
        self.blur()

    def blur(self):
        if self.need_blur_cb_var.get():
            blur_top_level(self.top_level)

    def no_blur(self):
        self.top_level.config(bg=self.default_color)

    def refresh_topmost(self):
        self.top_level.lift()  # 提升到顶层
        self.top_level.attributes('-topmost', True)
        self.top_level.after(300, self.refresh_topmost)


class RootWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Subtitle Mask')
        self.floating_window = FloatingWindow(self.root)
        self.root.withdraw()

    def run(self):
        self.root.mainloop()


app = RootWindow()
app.run()
