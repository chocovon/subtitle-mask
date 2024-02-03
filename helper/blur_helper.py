import win32gui
from BlurWindow.blurWindow import GlobalBlur


def blur_top_level(top_level):
    top_level.config(bg='green')
    top_level.wm_attributes("-transparent", 'green')
    top_level.update()

    wid = top_level.winfo_id()
    real_wid = win32gui.GetParent(wid)
    GlobalBlur(real_wid)
