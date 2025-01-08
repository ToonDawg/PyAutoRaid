from tkinter import Tk
from logging import Logger
import os
import platform
import subprocess
import time
import pygetwindow as gw
import sys
from Modules.arena.DailyTenArenaCommand import DailyTenClassicArenaCommand
from Modules.arena.TagTeamArenaCommand import TagTeamArenaCommand
from Modules.clan_boss.ClanBossCommand import ClanBossCommand
from Modules.daily_quests.DailyQuests import DailyQuestsCommand
from Modules.daily_quests.RewardsCommand import RewardsCommand
from Modules.doom_tower.DoomTower import DoomTowerCommand
from Modules.dungeons.IronTwins import IronTwinsCommand
from Modules.faction_wars.FactionWars import FactionWarsCommand
from utils.command_factory import CommandFactory, CommandKeys
from utils.click_handler import ClickHandler
import configparser
import datetime

from utils.config_handler import ConfigHandler


class PyAutoRaid:
    def __init__(self, tk_root: Tk, logger: Logger):
        self.tk_root = tk_root
        self.logger = logger
        self.command_factory = CommandFactory(self, logger)
        self.click_handler = ClickHandler(logger)
        self.config_handler = ConfigHandler()
        self.steps = {}

        # Register commands
        self.command_factory.register_command(CommandKeys.REWARDS, "Collect Rewards", RewardsCommand)
        self.command_factory.register_command(CommandKeys.DAILY_QUESTS, "Daily Quests", DailyQuestsCommand)
        self.command_factory.register_command(CommandKeys.TAG_TEAM_ARENA, "Tag Team Arena", TagTeamArenaCommand)
        self.command_factory.register_command(CommandKeys.FACTION_WARS, "Faction Wars", FactionWarsCommand)
        self.command_factory.register_command(CommandKeys.IRON_TWINS, "Iron Twins", IronTwinsCommand)
        self.command_factory.register_command(CommandKeys.DOOM_TOWER, "Doom Tower", DoomTowerCommand)
        self.command_factory.register_command(CommandKeys.CLANBOSS, "Clan Boss", ClanBossCommand)
        self.command_factory.register_command(CommandKeys.DAILY_TEN_CLASSIC_ARENA, "Classic Arena x 10", DailyTenClassicArenaCommand)

        # Initialization steps
        self.os = self.check_os()
        self.asset_path = self.get_asset_path()
        self.raid_path = self.find_raid_path()

        # Open and prepare the game
        self.make_sure_raid_is_open()

    def check_os(self):
        try:
            operating_system = platform.system()
            if operating_system != "Windows":
                self.logger.error("Unsupported OS detected. This program only works on Windows.")
                sys.exit(1)
            self.logger.info(f"Operating system detected: {operating_system}")
            return operating_system
        except Exception as e:
            self.logger.error(f"Error checking OS: {e}")
            raise

    def get_asset_path(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            while True:
                asset_path = os.path.join(current_dir, "assets")
                if os.path.exists(asset_path):
                    self.logger.info(f"Assets folder found: {asset_path}")
                    return asset_path

                # Move up one directory level
                new_dir = os.path.dirname(current_dir)
                if new_dir == current_dir:
                    self.logger.error("Assets folder not found.")
                    sys.exit(1)
                current_dir = new_dir
        except Exception as e:
            self.logger.error(f"Error finding assets path: {e}")
            raise

    def find_raid_path(self):
        try:
            appdata_local = os.getenv("LOCALAPPDATA")
            base_path = os.path.join(appdata_local, "PlariumPlay", "StandAloneApps", "raid-shadow-legends")

            # Recursively search for Raid.exe
            for root, dirs, files in os.walk(base_path, topdown=True):
                if "Raid.exe" in files:
                    raid_path = os.path.join(root, "Raid.exe")
                    self.logger.info(f"Raid executable found at: {raid_path}")
                    return raid_path

            self.logger.error("Raid executable not found. Please ensure it is installed.")
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Error finding Raid executable: {e}")
            raise

    def make_sure_raid_is_open(self):
        try:
            game_windows = gw.getWindowsWithTitle("Raid: Shadow Legends")
            if not game_windows:
                self.logger.info("Raid is not running. Attempting to open the game.")
                self.open_raid()
            else:
                self.logger.info("Raid is already running. Configuring the window.")
                self.configure_game_window()
        except Exception as e:
            self.logger.error(f"Error ensuring Raid is open: {e}")
            raise

    def open_raid(self):
        try:
            subprocess.Popen(
                [
                    os.path.join(self.raid_path, "PlariumPlay.exe"),
                    "--args",
                    "-gameid=101",
                    "-tray-start",
                ]
            )
            self.logger.info("Opening Raid via PlariumPlay...")
            time.sleep(10)
            self.configure_game_window()
        except Exception as e:
            self.logger.error(f"Error opening Raid: {e}")
            raise

    def configure_game_window(self):
        try:
            game_windows = gw.getWindowsWithTitle("Raid: Shadow Legends")
            if not game_windows:
                self.logger.warning("Raid window not found. Skipping configuration.")
                return

            raid_window = game_windows[0]
            raid_window.restore()
            raid_window.resizeTo(900, 600)
            raid_window.moveTo(500, 200)
            raid_window.activate()
            
            self.logger.info("Raid window resized and centered successfully.")
        except Exception as e:
            self.logger.error(f"Error configuring game window: {e}")
            raise

    def run_task(self, key: CommandKeys):
        self.configure_game_window()
        command = self.command_factory.get_command(key)
        if command:
            self.click_handler.back_to_bastion()
            command.execute()
