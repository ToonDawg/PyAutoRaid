import time
import pyautogui
from utils.base_command import CommandBase
from utils.click_handler import ClickHandler

class DoomTowerCommand(CommandBase):
    def execute(self):
        """Main execution method for the Doom Tower task."""
        try:
            self.logger.info("Starting Doom Tower task.")
            self.click_handler.delete_popup()
            # Navigate to Doom Tower
            if not self.navigate_to_doom_tower():
                self.logger.error("Failed to navigate to Doom Tower. Exiting task.")
                return

            # Complete battles
            self.complete_doom_tower_battles()

            # Handle boss stages
            self.handle_boss_stages()
            
            # Attempt stages one last time, incase of spare keys
            self.complete_doom_tower_battles()

            self.click_handler.back_to_bastion()
            self.logger.info("Doom Tower task completed successfully.")
        except Exception as e:
            self.logger.error(f"Error in DoomTowerCommand: {e}", exc_info=True)
            self.click_handler.back_to_bastion()

    def navigate_to_doom_tower(self):
        """Navigate to the Doom Tower screen."""
        if not self.click_handler.click_image("battleBTN.png", "Battle button"):
            return False
        self.click_handler.swipe_left()
        return self.click_handler.click_image("doomTower.png", "Doom Tower button")

    def complete_doom_tower_battles(self):
        """Complete Doom Tower battles."""
        while self.click_handler.wait_for_image("doomTowerNextStage.png", "Doom Tower Next Stage", timeout=5):
            if not self.click_handler.click_image("doomTowerNextStage.png", "Doom Tower Next Stage"):
                break

            if not self.click_handler.click_image("doomTowerStartBattle.png", "Doom Tower Start Battle"):
                self.logger.info("Not enough keys to continue battles. Exiting loop.")
                break

            # Check if we are still on the same screen after clicking 'Start Battle'
            if self.click_handler.wait_for_image("doomTowerStartBattle.png", "Doom Tower Start Battle", timeout=3):
                self.logger.info("Detected on the same screen after clicking 'Start Battle'. Assuming no keys.")
                pyautogui.press("esc")
                break

            # Wait for either battle completion or the 'Next Stage' button to reappear
            battle_completed = self.click_handler.wait_for_multi_battle_completion()
            if not battle_completed:
                self.logger.warning("Battle did not complete as expected.")
                pyautogui.press("esc")
                return

    def handle_boss_stages(self):
        """Handle boss stages in the Doom Tower."""
        if self.click_handler.wait_for_image("doomTowerScreen.png", "Doom Tower Stages Screen", timeout=5):
            self.logger.info("Handling boss stage right side...")
            pyautogui.click(1260, 530)
            time.sleep(2)
            self.logger.info("Handling boss stage 120...")
            pyautogui.click(950, 530)
            time.sleep(2)
        
        # Check if we are still on the same screen after clicking 'Start Battle'
        if not self.click_handler.click_image("doomTowerStartBattle.png", "Doom Tower Start Battle"):
            self.logger.info("Not enough keys to continue battles. Exiting loop.")
            return
        
        self.click_handler.wait_for_battle_completion()
        # Return to Stage Selection
        pyautogui.press("esc")
        
