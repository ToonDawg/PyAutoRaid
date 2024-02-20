import pyautogui, platform, tkinter, logging, os, sys,subprocess,time,random,configparser,pygetwindow,datetime
from screeninfo import Monitor, get_monitors
from tkinter import messagebox
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from ttkthemes import ThemedTk
import threading
import win32gui
class Daily:
    def __init__(self,master):
        self.running = True
        self.master = master
        logging.basicConfig(filename='Logging.log', format='%(levelname)s:%(message)s', encoding='utf-8', level=logging.DEBUG)
        # Clear the existing log file
        with open('Logging.log', 'w'):
            pass
        self.steps = {}
        self.OS = self.Check_os()  # Call the method here
        self.raidLoc = self.find_raid_path()
        self.asset_path=self.get_asset_path()
        self.folders_for_exe()
        if len(pygetwindow.getWindowsWithTitle("Raid: Shadow Legends")) < 1:
            self.open_raid()
        else:
            self.initiate_raid(False)
        os.system("taskkill /f /im PlariumPlay.exe")
        self.classic_battles = 0
        self.AS_bought=0
        self.MS_bought=0
        self.width=0
        self.height=0
        self.GR_upgrades=0
        self.quests_completed=0
        self.config = configparser.ConfigParser()
        self.utc_now = datetime.datetime.now(datetime.timezone.utc)
        self.utc_now_hour=self.utc_now.hour
        self.utc_now_str = self.utc_now.strftime("%d/%m/%Y")
        self.config_file(self.utc_now_str)
        self.manual_run_triggered=False
        self.settings_config=dict(self.config.items("Settings"))
        self.yesterday_utc=self.utc_now- datetime.timedelta(days=1)
        self.yesterday_now_str = self.yesterday_utc.strftime("%d/%m/%Y")
        self.two_days_ago=self.utc_now- datetime.timedelta(days=2)
        self.two_days_ago_str = self.two_days_ago.strftime("%d/%m/%Y")
        self.today_utc_str=self.utc_now.strftime("%d/%m/%Y")
        self.config.read('PARconfig.ini')
        configdate=self.config.get('Settings', 'utc_today')
        if (self.yesterday_now_str==configdate) and (self.utc_now_hour>=10):
            self.config_file(self.utc_now_str,True)
        if (self.two_days_ago_str==configdate) and (self.utc_now_hour>=10):
            self.config_file(self.utc_now_str,True)
        if (self.today_utc_str==configdate) and (self.utc_now_hour<=10):
            self.config_file(self.utc_now_str,True)



    def trigger_manual_run(self,TF):
        self.manual_run_triggered = TF

    def run(self):
        while self.running:
            # Re-read the config file to update the settings
            self.config.read('PARconfig.ini')
            self.ToDo = dict(self.config.items("Settings"))
            self.settings_config = dict(self.config.items("Settings"))

            if self.settings_config.get("automated_mode".lower().replace(' ', '_'), 'False') == 'True':
                try:
                    for key in self.ToDo:
                        if self.ToDo[key].lower() == 'true':  # Make sure to compare with 'true'
                            if key=='clanboss':
                                key='ClanBoss'
                            method_to_call = getattr(self, key, None)
                            if method_to_call:
                                method_to_call()
                            else:
                                print(f"Method for {key} not found.")
                    self.close_gui()
                    os.system("taskkill /f /im Raid.exe")
                    # sys.exit()
                    break
                except:
                    self.close_gui()
                    os.system("taskkill /f /im Raid.exe")
                    # sys.exit()
                    break
            else:
                if self.manual_run_triggered:
                    for key in self.ToDo:
                        
                        if self.ToDo[key].lower() == 'true':  # Make sure to compare with 'true'
                            if key=='clanboss':
                                key='ClanBoss'
                            method_to_call = getattr(self, key, None)
                            if method_to_call:
                                method_to_call()
                            else:
                                print(f"Method for {key} not found.")
                    self.trigger_manual_run(False)
            time.sleep(1)  # Sleep to prevent busy waiting
            
    def close_gui(self):
        if self.master:
            self.master.after(0, self.master.destroy)
            # self.master.after(0, sys.exit)

    def folders_for_exe(self):
        if getattr(sys, 'frozen', False):
            # The application is frozen
            self.asset_path = os.path.join(sys._MEIPASS, 'assets')
            self.steps["Exe_path"]="True"
            return True
        else:
            self.steps["Exe_path"]="False"
            return False

    def Check_os(self):
        operating_system = platform.system()
        if operating_system == "Windows":
            self.steps["OS"]="True"
            return operating_system
        else:
            tkinter.messagebox.showerror(
                "Error",
                "Unrecognized operating system (WINDOWS ONLY)",
            )
            logging.error("Identified this computer as something other than Windows operating system. This program only works with Windows.")
            sys.exit(1)

    def find_raid_path(self):
        appdata_local = os.path.join(os.environ['LOCALAPPDATA'])
        raid_feature = "Raid.exe"
        for root, dirs, files in os.walk(appdata_local):
            if raid_feature in dirs or raid_feature in files:
                raidloc = os.path.join(root, raid_feature)
                logging.debug(f"Found Raid.exe installed at {raidloc}")
                self.steps["Raid_path"]="True"
                return raidloc
        self.steps["Raid_path"]="False"
        logging.error("Raid.exe was not found.")
        sys.exit(1)
    
    def get_asset_path(self):
        # Start with the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        while True:
            # Construct the path to the assets folder
            self.asset_path = os.path.join(current_dir, 'assets')

            # Check if the assets path exists
            if os.path.exists(self.asset_path):
                self.steps["Asset_path"]="True"
                return self.asset_path

            # Move up one directory level
            new_dir = os.path.dirname(current_dir)
            if new_dir == current_dir:
                # We are at the root directory and didn't find the assets folder
                return None
            assets_second_path=os.path.join(new_dir, 'assets')
            if os.path.exists(assets_second_path):
                self.steps["Asset_path"]="True"
                return assets_second_path
            self.steps["Asset_path"]="False"
            if self.folders_for_exe() ==False:
                logging.error("Could not find the assets folder. This folder contains all of the images needed for this program to use. It must be in the same folder as this program.")
                sys.exit(1)

    def config_file(self,day,adjust=False):
        if os.path.exists("PARconfig.ini"):
            self.config.read('PARconfig.ini')
        else:
            self.config['Settings'] = {'UTC_today':day,'rewards': True,'ClanBoss':True,'automated_mode':True,'daily_ten_classic_arena':True}
            self.config['PlannedClanBossFightsToday'] = {'Easy': 0,
            'Normal': 0,'Hard': 0,'Brutal': 0,'Nightmare': 1,'Ultra-Nightmare': 3}
            self.config['ActualClanBossFightsToday'] = {'Easy': 0,
            'Normal': 0,'Hard': 0,'Brutal': 0,'Nightmare': 0,'Ultra-Nightmare': 0}
            self.config['XYclanbossCoordinates'] = {'EasyX': 1080,'EasyY': 'IDK Coords yet'
            ,'NormalX': 1080,'NormalY': 'IDK Coords yet','HardX': 1080,'HardY': 'IDK Coords yet','BrutalX': 1080,'BrutalY': 647,'NightmareX': 1080,'NightmareY': 724,'Ultra-NightmareX': 1080,'Ultra-NightmareY': 690}
            with open('PARconfig.ini', 'w') as configfile:
                self.config.write(configfile)
        if adjust:
            self.config['Settings'] = {'UTC_today':day,'rewards': self.settings_config['rewards'],'ClanBoss':self.settings_config['clanboss'],'automated_mode':self.settings_config['automated_mode'],'daily_ten_classic_arena':self.settings_config['daily_ten_classic_arena']}
            self.config['ActualClanBossFightsToday'] = {'Easy': 0,
            'Normal': 0,'Hard': 0,'Brutal': 0,'Nightmare': 0,'ultra-nightmare': 0}
            with open('PARconfig.ini', 'w') as configfile:
                self.config.write(configfile)

    def open_raid(self):
        subprocess.Popen(
            [
                os.path.join(os.getenv("LOCALAPPDATA"), "PlariumPlay\PlariumPlay.exe"),
                "--args",
                "-gameid=101",
                "-tray-start",
            ]
        )
        self.wait_for_game_window(title="Raid: Shadow Legends", timeout=100)  # Example title and timeout

    def wait_for_game_window(self, title, timeout):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if pyautogui.getWindowsWithTitle(title):
                logging.debug("Game window found, game should be loading in now.")
                self.steps["Open_raid"]="True"
                self.initiate_raid(True)
                return
            time.sleep(5)  # Wait for 5 seconds before checking again
        self.steps["Open_raid"]="False"
        logging.error("Raid took too long to open, game window not found.")
        sys.exit(1)
    
    def delete_popup(self):
        while (
            pyautogui.locateOnScreen(
                self.asset_path + "\\exitAdd.png",
                confidence=0.8,
            )
            != None
        ):
            adx, ady = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\exitAdd.png",
                confidence=0.8,
            )
            pyautogui.click(adx, ady)
            time.sleep(1)

    
    def back_to_bastion(self):
        while (
            pyautogui.locateOnScreen(
                self.asset_path + "\\goBack.png",
                confidence=0.8,
            )
            != None
        ):
            bastionx, bastiony = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\goBack.png",
                confidence=0.8,
            )
            pyautogui.click(bastionx, bastiony)
            time.sleep(2)

    def get_screen_info(self):
        for m in get_monitors():
            self.width = m.width
            self.height = m.height
            main = m.is_primary
            if self.width != 1920 or self.height != 1080:
                tkinter.messagebox.showerror(
                        "Warning",
                        "Your Screen pixel is not 1920 by 1080. This may cause issues",
                    )
            if main == True:
                center_width = int((self.width / 2) - 450)
                center_height = int((self.height / 2) - 300)
                return (center_width, center_height)
            
    def window_sizing_centering(self):
        center = self.get_screen_info()
        try:
            win = pygetwindow.getWindowsWithTitle("Raid: Shadow Legends")[0]
            if win:
                # Minimize and then maximize the window
                win.minimize()
                win.restore()
            else:
                print("No window found with the title 'Raid: Shadow Legends'")
            win.size = (900, 600)
            win.moveTo(center[0], center[1])       
        except:
            time.sleep(20)
            win = pygetwindow.getWindowsWithTitle("Raid: Shadow Legends")[0]
            win.size = (900, 600)
            win.moveTo(center[0], center[1])

    def initiate_raid(self,not_open):
        self.window_sizing_centering()
        if not_open:
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\exitAdd.png",
                    confidence=0.8,
                )
                == None
            ):
                pass
        self.back_to_bastion()
        self.delete_popup()
        self.steps["Initiate_raid"]="True"
        # os.system("taskkill /f /im PlariumPlay.exe")
#################################################################################################################
    def rewards(self):
        self.daily_gem_mine()
        self.daily_market_purchase()
        self.daily_shop()
        self.daily_guardian_ring()
        self.daily_clan()
        self.daily_timed_rewards()
        self.daily_quest_claims()
        self.daily_inbox()

    def daily_gem_mine(self):
        # Gem Mine
        pyautogui.click(583, 595)
        time.sleep(2)
        pyautogui.hotkey("esc")  # esc gem mine
        time.sleep(2)
        self.steps["Gem_mine"]="True"
        self.delete_popup()

    def daily_market_purchase(self):
        self.delete_popup()
        time.sleep(5)
        if pyautogui.locateOnScreen(
            self.asset_path + "\\theMarket.png",
            confidence=0.8,
        ):
            theMarketx, theMarkety = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\theMarket.png",
                confidence=0.8,
            )
            pyautogui.click(theMarketx, theMarkety)
            time.sleep(2)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\shopShard.png",
                    confidence=0.8,
                )
                != None
            ):
                shopShardx, shopShardy = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\shopShard.png",
                    confidence=0.8,
                )
                pyautogui.click(shopShardx, shopShardy,)
                time.sleep(2)
                self.steps["Market"]="Opened"
                self.steps["Market_purchases"]="None"
                while (
                    pyautogui.locateOnScreen(
                        self.asset_path + "\\getShard.png",
                        confidence=0.8,
                    )
                    != None
                ):
                    getShardx, getShardy = pyautogui.locateCenterOnScreen(
                        self.asset_path + "\\getShard.png",
                        confidence=0.8,
                    )
                    pyautogui.click(getShardx, getShardy,duration=2)
                    self.MS_bought+=1
                    continue
                
                time.sleep(2)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\marketAS.png",
                    confidence=0.8,
                )
                != None
            ):
                marketASx, marketASy = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\marketAS.png",
                    confidence=0.8,
                )
                pyautogui.click(marketASx, marketASy)
                time.sleep(2)
                while (
                    pyautogui.locateOnScreen(
                        self.asset_path + "\\getAS.png",
                        confidence=0.8,
                    )
                    != None
                ):
                    getASx, getASy = pyautogui.locateCenterOnScreen(
                        self.asset_path + "\\getAS.png",
                        confidence=0.8,
                    )
                    pyautogui.click(getASx, getASy)
                    self.AS_bought+=1
                    continue
                
                time.sleep(2)
            self.steps["Market_purchases"]=f"{self.MS_bought} mystery shards purchased, and {self.AS_bought} ancient shards purchased"
            self.back_to_bastion()
            self.delete_popup()
        
    def daily_shop(self):
        self.steps["Shop_claimed"]=[]
        if pyautogui.locateOnScreen(
            self.asset_path + "\\shopBTN.png",
            confidence=0.8,
        ):
            shopBTNx, shopBTNy = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\shopBTN.png",
                confidence=0.8,
            )
            pyautogui.click(shopBTNx, shopBTNy)
            time.sleep(2)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\claimAS.png",
                    confidence=0.8,
                )
                != None
            ):
                claimASx, claimASy = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\claimAS.png",
                    confidence=0.8,
                )
                pyautogui.click(claimASx, claimASy)
                time.sleep(2)
                while (
                    pyautogui.locateOnScreen(
                        self.asset_path + "\\defaultClaim.png",
                        confidence=0.8,
                    )
                    != None
                ):
                    defaultClaimx, defaultClaimy = pyautogui.locateCenterOnScreen(
                        self.asset_path + "\\defaultClaim.png",
                        confidence=0.8,
                    )
                    pyautogui.click(defaultClaimx, defaultClaimy)
                    self.steps["Shop_claimed"].append("Ancient Shard")
                    time.sleep(3)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\claimMS.png",
                    confidence=0.8,
                )
                != None
            ):
                claimMSx, claimMSy = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\claimMS.png",
                    confidence=0.8,
                )
                pyautogui.click(claimMSx, claimMSy)
                time.sleep(5)
                while (
                    pyautogui.locateOnScreen(
                        self.asset_path + "\\defaultClaim.png",
                        confidence=0.8,
                    )
                    != None
                ):
                    defaultClaimx, defaultClaimy = pyautogui.locateCenterOnScreen(
                        self.asset_path + "\\defaultClaim.png",
                        confidence=0.8,
                    )
                    pyautogui.click(defaultClaimx, defaultClaimy)
                    self.steps["Shop_claimed"].append("Mystery Shard")
                    time.sleep(3)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\offers.png",
                    confidence=0.9,
                )
                != None
            ):
                offersx, offersy = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\offers.png",
                    confidence=0.8,
                )
                pyautogui.click(offersx, offersy)
                time.sleep(3)
                #Click through all offers
                for i in range(724,1400,50):
                    pyautogui.click(i, 333)
                    if pyautogui.locateOnScreen(
                        self.asset_path + "\\claimFreeGift.png",
                        confidence=0.8,
                    ):
                        freegiftx, freegifty = pyautogui.locateCenterOnScreen(
                            self.asset_path + "\\claimFreeGift.png",
                            confidence=0.8,
                        )
                        pyautogui.click(freegiftx, freegifty)
                        self.steps["Shop_claimed"].append("Free Gift")
                        time.sleep(1)
                time.sleep(1.5)
            self.back_to_bastion()
            self.delete_popup()

    def daily_guardian_ring(self):
        # GUARDIAN RING - Upgrade champions
        if pyautogui.locateOnScreen(
            self.asset_path + "\\guardianRing.png",
            confidence=0.8,
        ):
            guardianRingx, guardianRingy = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\guardianRing.png",
                confidence=0.8,
            )
            pyautogui.click(guardianRingx, guardianRingy)
            time.sleep(4)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\GRupgrade.png",
                    confidence=0.8,
                )
                != None
            ):
                GRupgradex, GRupgradey = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\GRupgrade.png",
                    confidence=0.8,
                )
                pyautogui.click(GRupgradex, GRupgradey)
                self.GR_upgrades+=1
                time.sleep(2)
            self.steps["GR_upgrades"]= self.GR_upgrades
            self.back_to_bastion()
            self.delete_popup()

    def daily_timed_rewards(self):
        # TIME REWARDS
        if pyautogui.locateOnScreen(
            self.asset_path + "\\timeRewards.png",
            confidence=0.8,
        ):
            timeRewardsx, timeRewardsy = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\timeRewards.png",
                confidence=0.8,
            )
            pyautogui.click(timeRewardsx, timeRewardsy)
            time.sleep(2)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\redNotificationDot.png",
                    confidence=0.8,
                )
                != None
            ):
                redx, redy = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\redNotificationDot.png",
                    confidence=0.8,
                )
                pyautogui.click(redx, redy)
                time.sleep(1)
            for i in range(669,1269,100):
                time.sleep(0.2)
                pyautogui.click(i, 500)
            time.sleep(1)
            pyautogui.click(1269, 500)
            pyautogui.click(1269, 500)
            self.steps["Timed_rewards"]="Collected"
            self.back_to_bastion()
            self.delete_popup()
        self.steps["7_campaign_battles"]="Not Collected"

    def daily_clan(self):
        if pyautogui.locateOnScreen(
            self.asset_path + "\\clanBTN.png",
            confidence=0.8,
        ):
            clanBTNx, clanBTNy = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\clanBTN.png",
                confidence=0.8,
            )
            pyautogui.click(clanBTNx, clanBTNy)
            time.sleep(1)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\clanMembers.png",
                    confidence=0.8,
                )
                != None
            ):
                clanMembersx, clanMembersy = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\clanMembers.png",
                    confidence=0.8,
                )
                pyautogui.click(clanMembersx, clanMembersy)
                time.sleep(1)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\clanCheckIn.png",
                    confidence=0.8,
                )
                != None
            ):
                clanCheckInx, clanCheckIny = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\clanCheckIn.png",
                    confidence=0.8,
                )
                pyautogui.click(clanCheckInx, clanCheckIny)
                time.sleep(1)
            if pyautogui.locateOnScreen(
                self.asset_path + "\\clanTreasure.png",
                confidence=0.8,
            ):
                clanTreasurex, clanTreasurey = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\clanTreasure.png",
                    confidence=0.8,
                )
                pyautogui.click(clanTreasurex, clanTreasurey)
                time.sleep(1)
            if (
                pyautogui.locateAllOnScreen(
                    self.asset_path + "\\redNotificationDot.png",
                    confidence=0.8,
                )
                != None
            ):
                for dotsx, doty, z, c in pyautogui.locateAllOnScreen(
                    self.asset_path + "\\redNotificationDot.png",
                    confidence=0.8,
                ):
                    pyautogui.click(dotsx, doty + 10)
                    time.sleep(3)
            self.steps["Daily_clan"]="Accessed"
            self.back_to_bastion()

    def daily_quest_claims(self):
        # QUESTS - Check for completed daily and advanced quests and claim
        if pyautogui.locateOnScreen(
            self.asset_path + "\\quests.png",
            confidence=0.8,
        ):
            questsx, questsy = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\quests.png",
                confidence=0.8,
            )
            pyautogui.click(questsx, questsy)
            time.sleep(2)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\questClaim.png",
                    confidence=0.8,
                )
                != None
            ):
                questClaimx, questClaimy = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\questClaim.png",
                    confidence=0.8,
                )
                pyautogui.click(questClaimx, questClaimy)
                self.quests_completed+=1
                time.sleep(1)
            if pyautogui.locateOnScreen(
                self.asset_path + "\\advancedQuests.png",
                confidence=0.8,
            ):
                advancedQuestsx, advancedQuestsy = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\advancedQuests.png",
                    confidence=0.8,
                )
                pyautogui.click(advancedQuestsx, advancedQuestsy)
                self.quests_completed+=1
                time.sleep(1)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\questClaim.png",
                    confidence=0.8,
                )
                != None
            ):
                questClaimx, questClaimy = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\questClaim.png",
                    confidence=0.8,
                )
                pyautogui.click(questClaimx, questClaimy)
                self.quests_completed+=1
                time.sleep(1)
            self.steps["Quests_completed"]=self.quests_completed
            self.back_to_bastion()
            self.delete_popup()
        else:
            self.steps["Quests_Completed"]="Not Accessed"

    def daily_inbox(self):
        time.sleep(1)
        pyautogui.hotkey("i")
        inbox_items=["inbox_energy","inbox_brew","inbox_purple_forge","inbox_yellow_forge","inbox_coin","inbox_potion"]
        for i in inbox_items:
            png=f"\\{i}.png"
            time.sleep(0.3)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + png,
                    confidence=0.7,
                )
                != None
            ):
                energy = pyautogui.locateOnScreen(
                    self.asset_path + png,
                    confidence=0.7,
                )

                pyautogui.moveTo(energy)
                pyautogui.moveRel(250, 0)
                pyautogui.click()
                time.sleep(2)
        self.steps["daily_inbox"]= "Accessed"
        self.back_to_bastion()
        self.delete_popup()
#Rewards ^^
##########################################################################

    def daily_ten_classic_arena(self):
        self.delete_popup()
        while (
        pyautogui.locateOnScreen(
            self.asset_path + "\\battleBTN.png",
            confidence=0.8,
        )
        != None
    ):
            battlex, battley = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\battleBTN.png",
                confidence=0.9,
            )
            pyautogui.click(battlex, battley)
            time.sleep(2)
        while (
            pyautogui.locateOnScreen(
                self.asset_path + "\\arenaTab.png",
                confidence=0.8,
            )
            != None
        ):
            battlex, battley = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\arenaTab.png",
                confidence=0.9,
            )
            pyautogui.click(battlex, battley)
            time.sleep(2)
        while (
            pyautogui.locateOnScreen(
                self.asset_path + "\\classicArena.png",
                confidence=0.8,
            )
            != None
        ):
            battlex, battley = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\classicArena.png",
                confidence=0.9,
            )
            pyautogui.click(battlex, battley)
            time.sleep(2)
            regions=[[1215, 423, 167, 58,[1304, 457]],[1215, 508, 167, 58,[1304, 540]],[1215, 596, 167, 58,[1303, 625]],[1215, 681, 167, 58,[1304, 711]],[1208, 762, 190, 68,[1304, 800]]] #?
            for j in range(0,2):
                while (
                            pyautogui.locateOnScreen(
                                self.asset_path + "\\arenaRefresh.png",
                                confidence=0.8,
                            )
                            != None
                        ):
                            battlex, battley = pyautogui.locateCenterOnScreen(
                                self.asset_path + "\\arenaRefresh.png",
                                confidence=0.9,
                            )
                            pyautogui.click(battlex, battley)
                            time.sleep(2)
                for i in regions:
                    
                    if (
                        pyautogui.locateOnScreen(
                            self.asset_path + "\\arenaBattle.png",
                            region=(i[0], i[1], i[2], i[3]),
                            confidence=0.6,
                        )
                        != None
                    ):
                        pyautogui.click(i[4][0], i[4][1])
                        time.sleep(3)
                        #Replenish tokens or quit if out of them
                        while (
                            pyautogui.locateOnScreen(
                                self.asset_path + "\\arenaConfirm.png",
                                confidence=0.8,
                            )
                            != None
                        ):
                            battlex, battley = pyautogui.locateCenterOnScreen(
                                self.asset_path + "\\arenaConfirm.png",
                                confidence=0.9,
                            )
                            pyautogui.click(battlex, battley)
                            print("confirm tokens")
                            time.sleep(5)
                            pyautogui.click(i[4][0], i[4][1])
                        if (
                            pyautogui.locateOnScreen(
                                self.asset_path + "\\classicArenaRefill.png",
                                confidence=0.8,
                            )
                            != None
                        ):
                            self.steps["Classic_Arena"]="Ran out of coins"
                            self.steps["classic_arena_battles"]=f"{self.classic_battles} total classic arena battles fought"
                            self.back_to_bastion()
                            self.delete_popup()
                            return
                        #
                        time.sleep(4)
                        if (
                            pyautogui.locateOnScreen(
                                self.asset_path + "\\arenaStart.png",
                                confidence=0.8,
                            )
                            != None
                        ):
                            battlex, battley = pyautogui.locateCenterOnScreen(
                                self.asset_path + "\\arenaStart.png",
                                confidence=0.9,
                            )
                            pyautogui.click(battlex, battley)
                        #first battle^^
                        while (
                            pyautogui.locateOnScreen(
                                self.asset_path + "\\tapToContinue.png",
                                confidence=0.8,
                            )
                            == None
                        ):
                            print("First time looking for continue")
                            time.sleep(1)
                        while (
                            pyautogui.locateOnScreen(
                                self.asset_path + "\\tapToContinue.png",
                                confidence=0.8,
                            )
                            != None
                        ):
                            time.sleep(1)
                            goBackx, goBacky = pyautogui.locateCenterOnScreen(
                                self.asset_path + "\\tapToContinue.png",
                                confidence=0.8,
                            )
                            pyautogui.click(goBackx, goBacky)
                            self.classic_battles +=1
                            print("finishing arena battle")
                            time.sleep(1)
                            pyautogui.click(goBackx, goBacky)
                            print("breaking first battle")
                            time.sleep(3)
                        if j ==1:
                            pyautogui.doubleClick(969, 788, interval=1)
                            pyautogui.dragRel(0,-381,duration=2)#DRAGGGGG
                            time.sleep(3)
                    time.sleep(1)
                    pyautogui.doubleClick(969, 788, interval=1)
                    
                time.sleep(1)
                if j ==0:
                    pyautogui.doubleClick(969, 788, interval=1)
                    pyautogui.dragRel(0,-380,duration=2)
                    time.sleep(3)    
        time.sleep(3)
                

        print(self.classic_battles)
        self.steps["classic_arena_battles"]=f"{self.classic_battles} total classic arena battles fought"
        self.back_to_bastion()
        self.delete_popup()
    
    


    def ClanBoss(self):
        CBDIFFICULTYS = ["ultra-nightmare", "nightmare", "brutal", "hard", "normal", "easy"]
        time.sleep(1.5)
        self.delete_popup()
        while (
            pyautogui.locateOnScreen(
                self.asset_path + "\\battleBTN.png",
                confidence=0.8,
            )
            != None
        ):
            battlex, battley = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\battleBTN.png",
                confidence=0.9,
            )
            pyautogui.click(battlex, battley)
            time.sleep(2)
        while (
            pyautogui.locateOnScreen(self.asset_path + "\\CB.png", confidence=0.9) != None
        ):
            CBx, CBy = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\CB.png", confidence=0.9
            )
            pyautogui.click(CBx, CBy)
            time.sleep(3)
        while (
            pyautogui.locateOnScreen(self.asset_path + "\\CB2.png", confidence=0.9) != None
        ):
            CB2x, CB2y = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\CB2.png", confidence=0.9
            )
            pyautogui.click(CB2x, CB2y)
            time.sleep(3)
        while (
            pyautogui.locateOnScreen(
                self.asset_path + "\\demonLord.png",
                confidence=0.9,
            )
            != None
        ):
            demonLordx, demonLordy = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\demonLord.png",
                confidence=0.8,
            )
            pyautogui.click(demonLordx, demonLordy)
            time.sleep(2)
        while (
            pyautogui.locateOnScreen(
                self.asset_path + "\\demonLord2.png",
                confidence=0.9,
            )
            != None
        ):
            demonLord2x, demonLord2y = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\demonLord2.png",
                confidence=0.8,
            )
            pyautogui.click(demonLord2x, demonLord2y)
            time.sleep(4)
        pyautogui.click(1080, 724)
        pyautogui.drag(0, -200, duration=1)
        while (
            pyautogui.locateOnScreen(
                self.asset_path + "\\CBreward.png",
                confidence=0.8,
            )
            != None
        ):
            CBrewardx, CBrewardy = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\CBreward.png",
                confidence=0.8,
            )
            time.sleep(2)
            pyautogui.click(CBrewardx, CBrewardy)
            time.sleep(2)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\nightmareClaimed.png",
                    confidence=0.8,
                )
                != None
            ):
                (
                    nightmareClaimedx,
                    nightmareClaimedy,
                ) = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\CBclaim.png",
                    confidence=0.5,
                )
                pyautogui.click(nightmareClaimedx, nightmareClaimedy)
                time.sleep(1)
                pyautogui.click()
                # the second click needs to recognize the continue
                time.sleep(1)
                pyautogui.click()
        while (
            pyautogui.locateOnScreen(
                self.asset_path + "\\CBclaim.png",
                confidence=0.8,
            )
            != None
        ):
            CBclaimx, CBclaimy = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\CBclaim.png",
                confidence=0.5,
            )
            pyautogui.click(CBclaimx, CBclaimy)
            time.sleep(1)
            pyautogui.click()
        time.sleep(2)
        pyautogui.click(1080, 724)
        pyautogui.drag(0, +200, duration=1)
        time.sleep(1)
        while (
            pyautogui.locateOnScreen(
                self.asset_path + "\\CBhard.png",
                confidence=0.8,
            )
            != None
        ):
            yCB=690
            xCB=1080
            difficulty = 'nightmare'
            for i in CBDIFFICULTYS:
                if self.config["ActualClanBossFightsToday"][i]<self.config["PlannedClanBossFightsToday"][i]:
                    yCB=int(self.config["XYclanbossCoordinates"][i+'y'])
                    xCB=int(self.config["XYclanbossCoordinates"][i+'x'])
                    difficulty = i
                    break
                
            if yCB == 690:
                pyautogui.click(1080, 724)
                pyautogui.drag(0, -200, duration=1)
                pyautogui.click(1080, 690)
            else:
                pyautogui.click(xCB, yCB)

            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\CBbattle.png",
                    confidence=0.8,
                )
                != None
            ):
                CBbattlex, CBbattley = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\CBbattle.png",
                    confidence=0.8,
                )
                time.sleep(2)
                pyautogui.click(CBbattlex, CBbattley)
                time.sleep(1)
                if (
                    pyautogui.locateOnScreen(
                        self.asset_path + "\\CBnokey.png",
                        confidence=0.8,
                    )
                    != None
                ):
                    break
            time.sleep(1)
        time.sleep(5)
        if (
            pyautogui.locateOnScreen(
                self.asset_path + "\\CBstart.png",
                confidence=0.8,
            )
            != None
        ):
            CBstartx, CBstarty = pyautogui.locateCenterOnScreen(
                self.asset_path + "\\CBstart.png",
                confidence=0.8,
            )
            time.sleep(2)
            pyautogui.click(CBstartx, CBstarty)
            time.sleep(1)
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\CBcontinue.png",
                    confidence=0.8,
                )
                != None
            ):
                CBcontinuex, CBcontinuey = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\CBcontinue.png",
                    confidence=0.8,
                )
                time.sleep(2)
                pyautogui.click(CBcontinuex, CBcontinuey)
                time.sleep(200)

            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\gotoBastion.png",
                    confidence=0.8,
                )
                == None
            ):
                pass
            while (
                pyautogui.locateOnScreen(
                    self.asset_path + "\\gotoBastion.png",
                    confidence=0.8,
                )
                != None
            ):
                gotoBastionx, gotoBastiony = pyautogui.locateCenterOnScreen(
                    self.asset_path + "\\gotoBastion.png",
                    confidence=0.8,
                )

                pyautogui.click(gotoBastionx, gotoBastiony)
                newactual = int(self.config['ActualClanBossFightsToday'][difficulty])
                newactual += 1
                self.config['ActualClanBossFightsToday'][difficulty] = str(newactual)
                with open('PARconfig.ini', 'w') as configfile:
                    self.config.write(configfile)
                time.sleep(2)
        # pyautogui.click(566, 790)
        self.delete_popup()
        self.back_to_bastion()
        self.delete_popup()
                
        if difficulty == "":
            difficulty = "No"
        return f"{difficulty} Clan boss fought"


class GUI:
    def __init__(self, master):
        self.app = Daily(master)  # Create the Daily instance
        self.timer_thread()
        self.daily_thread = threading.Thread(target=self.app.run)  # Create the thread
        self.daily_thread.start()  # Start the thread
        self.daily_thread.name="PAR"
        self.config = configparser.ConfigParser()
        self.config.read('PARconfig.ini')
        tasks_config = dict(self.config.items("Settings"))
        settings_config=dict(self.config.items("Settings"))
        self.master = master
        master.title("PyAutoRaid Task Selector")

        # Creating a ttk Frame which will contain all other widgets
        main_frame = ttk.Frame(master)
        main_frame.pack(fill=tkinter.BOTH, expand=True)
        config_keys=['rewards','daily_ten_classic_arena',
            'clanboss']
        # Automated Mode Checkbox
        self.automated_mode = tkinter.IntVar()
        if settings_config.get("automated_mode") == 'True':
            self.automated_mode.set(1)
        self.chk_automated_mode = ttk.Checkbutton(main_frame, text="Automated Mode", variable=self.automated_mode)
        self.chk_automated_mode.grid(row=0, column=0, padx=10, pady=(10,0), sticky="W")

        # Separator
        self.separator = ttk.Separator(main_frame, orient='horizontal')
        self.separator.grid(row=1, column=0, padx=10, pady=5, sticky="EW")

        def checkbox_callback(var_name, index, mode, config_key, var):
            updated_value = str(bool(var.get()))
            self.config['Settings'][config_key] = updated_value
            with open('PARconfig.ini', 'w') as configfile:
                self.config.write(configfile)

        # Other Checkboxes
        self.checkbox_texts = [
            "Collect Rewards", "Ten Classic Arena Battles", "Clan Boss",
        ]
        self.checkboxes = []
        self.vars = []
        
        for i, text in enumerate(config_keys, start=2):
            guiname=self.checkbox_texts[i-2]
            var = tkinter.IntVar()
            config_key = config_keys[i-2]
            if tasks_config.get(config_key, 'False') == 'True':
                var.set(1)
                # Set trace on the variable
            var.trace_add('write', lambda var_name, index, mode, var=var, config_key=config_key: checkbox_callback(var_name, index, mode, config_key, var))
            chk = ttk.Checkbutton(main_frame, text=guiname, variable=var)
            chk.grid(row=i, column=0, padx=10, pady=(0,5), sticky="W")
            self.checkboxes.append(chk)
            self.vars.append(var)
        # Buttons in the main_frame
        self.btn_manual_run = ttk.Button(main_frame, text="Manual Run", command=self.manual_run)
        self.btn_manual_run.grid(row=len(self.checkbox_texts) + 3, column=0, padx=10, pady=(5, 5), sticky="W")

        self.btn_quit_all = ttk.Button(main_frame, text="Quit All", command=self.quit_all)
        self.btn_quit_all.grid(row=len(self.checkbox_texts) + 3, column=1, padx=10, pady=(5, 5), sticky="E")
        # Create and start the Daily thread
        

    def manual_run(self):
    # Define what should happen when Manual Run is clicked
        if self.app:
            self.app.trigger_manual_run(True)

    def quit_all(self,timer=False):
        if timer:
            os.system("taskkill /f /im Raid.exe")
        os.system("taskkill /f /im DailyQuests.exe")
        os.system("taskkill /f /im PyAutoRaid.exe")
        os.system("taskkill /f /im python.exe")
        os.system("taskkill /f /im DailyQuests.py")
        os.system("taskkill /f /im PlariumPlay.exe")

    def timer_thread(self):
        timeout = 1800
        # Create a timer that will call quit_all() after the timeout
        self.timer = threading.Timer(timeout, lambda: self.quit_all(timer=True))
        self.timer.name = "timer_thread"
        self.timer.daemon = True
        # Start the timer
        self.timer.start()

def on_closing():
    if my_gui.quit_timer.is_alive():
        my_gui.quit_timer.cancel()
    if my_gui.daily_thread.is_alive():
        my_gui.daily_thread.join(timeout=1)
    root.destroy()

if __name__ == "__main__":
    root = ThemedTk(theme="equilux")
    root.geometry("500x560+10+240")

    my_gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)  # To ensure clean exit
    root.mainloop()
    