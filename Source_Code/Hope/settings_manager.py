import json

class SettingsManager:
    def __init__(self, filename='settings.json'):
        self.filename = filename
        self.settings = self.load_settings()
        
    def load_settings(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.default_settings()
        
    def save_settings(self):
        with open(self.filename, 'w') as f:
            json.dump(self.settings, f, indent=4)
            
    def default_settings(self):
        return {
            'fullscreen' : False,
            'borderless' : False,
            'volume' : 0.5
        }
        
    def get_settings(self, key):
        return self.settings.get(key)
    
    def update_settings(self, key, value):
        self.settings[key] = value
        self.save_settings()