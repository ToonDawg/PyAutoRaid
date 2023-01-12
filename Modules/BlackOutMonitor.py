# Black out the monitor in the end. Put it to sleep so ya boy can sleep
import sys
import time
import sqlite3 as sql
import pathlib
import os
import subprocess
import win32api
import win32con

DIR = os.getcwd()
DB_PATH = os.path.join(DIR, "Data", "Settings.db")
ASSETS_PATH = os.path.join(DIR, "assets")
connection = sql.connect(DB_PATH)
cursor = connection.cursor()


def BlackOutMonitor():
    cursor.execute("SELECT * FROM PyAutoRaid")
    results = cursor.fetchall()
    connection.commit()
    Run = results
    Run = Run[0][5]
    if Run == "True":
        time.sleep(2)
        if sys.platform.startswith("linux"):
            import os

            os.system("xset dpms force off")

        elif sys.platform.startswith("win"):
            win32api.SendMessage(
                win32con.HWND_BROADCAST,
                win32con.WM_SYSCOMMAND,
                win32con.SC_MONITORPOWER,
                2,
            )

        elif sys.platform.startswith("darwin"):

            subprocess.call(
                "echo 'tell application \"Finder\" to sleep' | osascript", shell=True
            )


if __name__ == "__main__":
    BlackOutMonitor()
