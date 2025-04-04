import json

WINDOW_DATA_PATH = 'window_data.json'


class WindowData:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.width = 800
        self.height = 100
        self.need_blur = True

    def load(self):
        try:
            with open(WINDOW_DATA_PATH, 'r') as file:
                raw_window_data = json.load(file)
                self.x = raw_window_data['x']
                self.y = raw_window_data['y']
                self.width = raw_window_data['width']
                self.height = raw_window_data['height']
                self.need_blur = raw_window_data['need_blur']
                print(raw_window_data)
                return True
        except FileNotFoundError:
            return False

    def save(self):
        with open(WINDOW_DATA_PATH, 'w') as file:
            json.dump(self.__dict__, file)


class LocalConfig:
    def __init__(self):
        self.first_open = True
        self.window_data = WindowData()
        if self.window_data.load():
            self.first_open = False

    def save_geo(self, geo_obj):
        self.window_data.x = geo_obj['x']
        self.window_data.y = geo_obj['y']
        self.window_data.width = geo_obj['width']
        self.window_data.height = geo_obj['height']
        self.window_data.save()

    def save_need_blur(self, need_blur):
        self.window_data.need_blur = need_blur
        self.window_data.save()

    def get_geo_str(self):
        wd = self.window_data
        x = str(wd.x)
        y = str(wd.y)
        width = str(wd.width)
        height = str(wd.height)
        return width + 'x' + height + '+' + x + '+' + y
