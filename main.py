import tkinter as tk
from tkinter import ttk


from helper.blur_helper import blur_top_level
from helper.keyboard_helper import KeyboardHelper
from helper.local_config import LocalConfig
from helper.mouse_move_monitor import MouseMoveMonitor


class FloatingWindow:
    def __init__(self, master):
        self.master = master
        self.top_level = top_level = tk.Toplevel(master)
        self.showing = True
        self.config = LocalConfig()
        self.default_color = self.top_level.cget('background')
        self.mouse_move_monitor = MouseMoveMonitor()
        self.mouse_move_monitor.register_on_enter(self.show_hints)
        self.mouse_move_monitor.register_on_leave(self.hide_hints)
        self.update_mouse_monitor_region()

        top_level.wm_attributes("-topmost", 1)
        top_level.overrideredirect(True)

        top_level.wm_geometry(self.get_geo_str())

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

        self.hint = tk.Label(top_level, text="Hold [Ctrl] or press [-] to hide / show.")

        if self.config.first_open:
            self.show_hints(init=True)

    def dragging(self, event):
        top_level = self.top_level
        x = event.x - self.lastClickX + top_level.winfo_x()
        y = event.y - self.lastClickY + top_level.winfo_y()
        top_level.geometry("+%s+%s" % (x, y))

    def on_mouse_down(self, event):
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

    def on_key_press(self, e):
        if e.name == '-':
            self.toggle()
        if 'ctrl' in e.name:
            self.hide()

    def on_key_release(self, e):
        if 'ctrl' in e.name:
            self.show()

    def on_mouse_release(self, _):
        geo_obj = {'x': self.top_level.winfo_x(),
                   'y': self.top_level.winfo_y(),
                   'width': self.top_level.winfo_width(),
                   'height': self.top_level.winfo_height()}
        self.save_geo(geo_obj)
        self.update_mouse_monitor_region()
        self.mouse_move_monitor.enable()

    def terminate(self):
        self.master.quit()
        quit()

    def get_geo_str(self):
        geo = self.config.get_window_data()
        x = str(geo['x'])
        y = str(geo['y'])
        width = str(geo['width'])
        height = str(geo['height'])
        return width + 'x' + height + '+' + x + '+' + y

    def save_geo(self, geo_obj):
        self.config.save_window_data(geo_obj)

    def update_mouse_monitor_region(self):
        geo = self.config.get_window_data()
        x = geo['x']
        y = geo['y']
        width = geo['width']
        height = geo['height']
        self.mouse_move_monitor.update_region(x, x + width, y, y + height)

    def show_hints(self, init=False):
        self.close_button.pack(side="top", anchor="ne")
        self.grip.pack(side="bottom", anchor="se")
        self.hint.pack(anchor="center")
        if not init:
            self.no_blur()

    def hide_hints(self):
        self.close_button.pack_forget()
        self.grip.pack_forget()
        self.hint.pack_forget()
        self.blur()

    def blur(self):
        blur_top_level(self.top_level)

    def no_blur(self):
        self.top_level.config(bg=self.default_color)


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
