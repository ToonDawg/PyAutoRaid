import configparser
import os
from datetime import datetime
from utils.command_factory import CommandKeys

class ConfigHandler:
    def __init__(self, config_file="PARconfig.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            self._create_default_config()
        else:
            self.config.read(config_file)

        # Ensure all CommandKeys enums are present in the Settings section
        self._initialize_enum_settings()

    def _create_default_config(self):
        """Creates a default configuration file if it doesn't exist."""
        self.config['Settings'] = {
            'utc_today': datetime.utcnow().strftime('%d/%m/%Y'),
            'rewards': 'True',
            'clanboss': 'False',
            'automated_mode': 'False',
            'daily_ten_classic_arena': 'True',
        }
        self.config['PlannedClanBossFightsToday'] = {
            'easy': '0',
            'normal': '0',
            'hard': '0',
            'brutal': '0',
            'nightmare': '1',
            'ultra-nightmare': '1',
        }
        self.config['ActualClanBossFightsToday'] = {
            'easy': '0',
            'normal': '0',
            'hard': '0',
            'brutal': '0',
            'nightmare': '0',
            'ultra-nightmare': '0',
        }
        self.save_config()

    def _initialize_enum_settings(self):
        """Ensures all CommandKeys enums are present in the Settings section."""
        if not self.config.has_section("Settings"):
            self.config.add_section("Settings")

        for command_key in CommandKeys:
            key = command_key.value
            if not self.config.has_option("Settings", key):
                self.config.set("Settings", key, "False") 
        self.save_config()

    def save_config(self):
        """Writes the current configuration to the file."""
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def read_setting(self, section, key):
        """Reads a specific setting."""
        if self.config.has_section(section) and self.config.has_option(section, key):
            return self.config.get(section, key)
        else:
            raise KeyError(f"'{key}' not found in section '{section}'")

    def update_setting(self, section, key, value):
        """Updates or adds a setting."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()

    def delete_setting(self, section, key):
        """Deletes a specific setting."""
        if self.config.has_section(section) and self.config.has_option(section, key):
            self.config.remove_option(section, key)
            self.save_config()
        else:
            raise KeyError(f"'{key}' not found in section '{section}'")

    def list_settings(self, section):
        """Lists all settings in a section."""
        if self.config.has_section(section):
            return dict(self.config.items(section))
        else:
            raise KeyError(f"Section '{section}' not found")
