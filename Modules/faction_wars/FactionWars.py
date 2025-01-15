import time
from utils.base_command import CommandBase


class FactionWarsCommand(CommandBase):
    def move_to_faction_position(self, direction):
        """Moves to the left or right to reveal factions."""
        self.logger.info(f"Swiping all the way to the {direction}.")
        if direction == "right":
            self.click_handler.swipe_left(800,1)
            time.sleep(1)
            self.click_handler.swipe_right(205, 1)
        elif direction == "left":
            self.click_handler.swipe_right(1400, 1)
        time.sleep(1)

    def execute(self):
        try:
            self.logger.info("Starting Faction Wars task.")
            
            # Collect rewards if bought something from the shop.
            

            faction_positions = {
                "right": [
                    {"name": "Dark Elf", "x": 560, "y": 600},
                    {"name": "High Elf", "x": 680, "y": 365},
                    {"name": "Sacred Order", "x": 760, "y": 470},
                    {"name": "Barbarian", "x": 870, "y": 610},
                    {"name": "Banner Lords", "x": 960, "y": 370},
                    {"name": "Dwarves", "x": 1080, "y": 480},
                    {"name": "Shadowkin", "x": 1250, "y": 600},
                    {"name": "Sylvan Watchers", "x": 1350, "y": 460},
                ],
                "left": [
                    {"name": "Lizardmen", "x": 670, "y": 480},
                    {"name": "Knight Revenant", "x": 800, "y": 610},
                    {"name": "Skinwalkers", "x": 800, "y": 350},
                    {"name": "Undead Hordes", "x": 950, "y": 500},
                    {"name": "Demonspawn", "x": 1060, "y": 350},
                    {"name": "Ogryn Tribes", "x": 1180, "y": 600},
                    {"name": "Orcs", "x": 1260, "y": 500},
                ],
            }

            # Close popups and navigate to Faction Wars
            self.logger.info("Attempting to close any existing pop-ups.")
            self.click_handler.delete_popup()

            self.click_handler.click_image("battleBTN.png", "Battle button")
            self.click_handler.click_image("factionWars.png", "Faction Wars option")

            # Process factions for both directions
            for direction, positions in faction_positions.items():
                self.move_to_faction_position(direction)
                for position in positions:
                    self.logger.debug(f"Attempting to select faction {position['name']} at ({position['x']}, {position['y']}).")
                    self.click_handler.click((position["x"], position["y"]), f"Selecting {position['name']} faction")
                    time.sleep(1)

                    # Start stage
                    self.start_stage()
                    time.sleep(2)

                    # If still on faction wars screen, faction is disabled
                    if self.click_handler._locate_image("factionWarsScreen.png", "Faction Wars Screen"):
                        continue

                    # Wait for multi-battle completion
                    self.click_handler.wait_for_multi_battle_completion()
                    self.return_to_faction_selection(direction)

            self.click_handler.back_to_bastion()
            self.logger.info("Faction Wars task completed successfully.")

        except Exception as e:
            self.logger.error(f"Error in FactionWarsCommand: {e}", exc_info=True)
            self.click_handler.back_to_bastion()

    def start_stage(self):
        """Starts a stage and handles multi-battle logic."""
        # Start stage
        while self.click_handler._locate_image("stageStart.png", "Stage Start Button"):
            self.logger.info("Stage Start Button detected. Preparing to select stage.")
            buttons = self.click_handler._locate_all_buttons("stageStart.png")
            if buttons:
                bottom_button = max(buttons, key=lambda b: b[1]) 
                bottom_x, bottom_y = bottom_button

                # Click on the bottom-most stage button
                self.click_handler.click((bottom_x, bottom_y), "Clicking bottom-most stage button")
                time.sleep(1)

                if self.click_handler._locate_image("stageStart.png", "Stage Start Button"):
                    self.logger.warning("Battle button still visible. Pressing ESC to go back.")
                    self.click_handler.press_key("esc", "Escape to cancel stage")
                    time.sleep(1)


        # Start multi-battle
        if self.click_handler._locate_image("multiBattleButton.png", "Multi-battle button detected"):
            self.click_handler.click_image("multiBattleButton.png", "Multi-battle button")
            self.click_handler.click_image("startMultiBattle.png", "Start Multi-battle")
            time.sleep(2)

    def return_to_faction_selection(self, direction):
        """Returns to faction selection after battle completion."""
        if self.click_handler._locate_image("multiBattleComplete.png", "Multi-battle Complete"):
            self.logger.info("Exiting multi-battle to faction selection.")
            self.app.actvate_game_window()
            while not self.click_handler.wait_for_image("factionWarsScreen.png", "FW screen", 1):
                self.click_handler.press_key("esc", "Pressing ESC to exit battle")

            # Move back to the correct faction position
            self.move_to_faction_position(direction)
