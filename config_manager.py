import json
import os

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self.get_default_config()
        
    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        
    def get_default_config(self):
        return {
            'start_key': 'F1',
            'stop_key': 'F2',
            'color': 'green',
            'position': 'top_right'
        }