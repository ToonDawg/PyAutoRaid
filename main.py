from tkinter import Tk
from app.pyAutoRaid import PyAutoRaid
from gui.main_gui import MainGUI
from utils.logger import setup_logger

if __name__ == "__main__":
    logger = setup_logger()
    root = Tk()
    pyAutoRaid = PyAutoRaid(root, logger)
    gui = MainGUI(root, pyAutoRaid)
    root.mainloop()