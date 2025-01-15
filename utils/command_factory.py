from enum import Enum
from logging import Logger
from typing import TYPE_CHECKING
from utils.click_handler import ClickHandler

if TYPE_CHECKING:
    from app.pyAutoRaid import PyAutoRaid
    
class CommandKeys(Enum):
    REWARDS = "rewards"
    DAILY_TEN_CLASSIC_ARENA = "daily_ten_classic_arena"
    CLANBOSS = "clanboss"
    FACTION_WARS = "faction_wars"
    IRON_TWINS = "iron_twins"
    DOOM_TOWER = "doom_tower"
    DAILY_QUESTS = "daily_quests"
    TAG_TEAM_ARENA = "tag_team_arena"

class CommandFactory:
    def __init__(self, daily_instance: 'PyAutoRaid', logger: Logger, click_handler: 'ClickHandler'):
        self.app = daily_instance
        self.logger = logger
        self.click_handler = click_handler
        self.registry = {}

    def register_command(self, key, display_name, command_class):
        self.logger.info(f"Registering command: {key}, Class: {command_class}")
        self.registry[key] = {
            "display_name": display_name,
            "command_class": command_class
        }


    def get_command(self, key):
        if key in self.registry:
            command_info = self.registry[key]
            self.logger.info(f"Fetching command: {key}, Class: {command_info['command_class']}")
            return command_info["command_class"](self.app, self.logger, self.click_handler)
        self.logger.warning(f"Command key not found: {key}")
        return None


    def get_display_names(self):
        return [(key, info["display_name"]) for key, info in self.registry.items()]
