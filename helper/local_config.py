import json

WINDOW_DATA_PATH = 'window_size.json'


class LocalConfig:
    def __init__(self):
        self.first_open = True
        self.window_data = {
            'x': 0,
            'y': 0,
            'width': 800,
            'height': 100
        }
        try:
            with open(WINDOW_DATA_PATH, 'r') as file:
                self.window_data = json.load(file)
                self.first_open = False
                print(self.window_data)
        except FileNotFoundError:
            pass

    def get_window_data(self):
        return self.window_data

    def save_window_data(self, window_data):
        self.window_data = window_data
        self._save()

    def _save(self):
        with open(WINDOW_DATA_PATH, 'w') as file:
            json.dump(self.window_data, file)
