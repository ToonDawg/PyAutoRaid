from tkinter import Tk
from app.pyAutoRaid import PyAutoRaid
from gui.main_gui import MainGUI
from utils.logger import setup_logger
from customtkinter import ctk_tk as ctk

if __name__ == "__main__":
    logger = setup_logger()
    root = ctk.CTk()
    pyAutoRaid = PyAutoRaid(root, logger)
    gui = MainGUI(root, pyAutoRaid)
    root.mainloop()