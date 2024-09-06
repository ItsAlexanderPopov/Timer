import json
import os

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
    
    # Load configuration from file if it exists
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
            default_config = self.get_default_config()
            default_config.update(loaded_config)
            return default_config
        else:
            return self.get_default_config()
        
    # Save the provided configuration to the config file
    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
    
    # Return a dictionary with default configuration values
    def get_default_config(self):
        return {
            'start_key': 'F1',
            'stop_key': 'F2',
            'kill_key': 'F3',
            'color': 'green',
            'position': 'top_right',
            'screen_index': 0
        }