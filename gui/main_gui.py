import logging
import threading
import tkinter as tk
from tkinter import ttk
from app.pyAutoRaid import PyAutoRaid
from utils.text_handler import TextHandler
from utils.config_handler import ConfigHandler  # Assuming ConfigHandler is implemented as described

class MainGUI:
    def __init__(self, root: tk.Tk, py_auto_raid_instance: PyAutoRaid):
        self.py_auto_raid = py_auto_raid_instance
        self.config_handler = ConfigHandler()
        self.root = root
        self.root.title("PyAutoRaid Task Selector")

        # Configure root to use a grid layout with weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=2)
        self.root.rowconfigure(1, weight=1)

        # Main frame for controls
        main_frame = ttk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="NSEW")

        # Logs frame
        logs_frame = ttk.Frame(root)
        logs_frame.grid(row=1, column=0, sticky="NSEW")

        # Automated Mode Checkbox
        self.automated_mode = tk.IntVar(value=int(self.config_handler.read_setting("Settings", "automated_mode")))
        automated_mode_label = ttk.Label(main_frame, text="Automated Mode")
        automated_mode_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="W")
        self.automated_mode_checkbox = ttk.Checkbutton(
            main_frame, text="Enable", variable=self.automated_mode, command=self.toggle_automated_mode
        )
        self.automated_mode_checkbox.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="W")

        # Dynamically create checkboxes based on registered commands
        self.checkbox_vars = {}
        for i, (command_key, display_name) in enumerate(self.py_auto_raid.command_factory.get_display_names()):
            # Read the value from the config file
            initial_value = int(self.config_handler.read_setting("Settings", command_key.value) == "True")
            var = tk.IntVar(value=initial_value)
            self.checkbox_vars[command_key] = var

            var.trace_add(
                'write',
                lambda var_name, index, mode, key=command_key, v=var: self.checkbox_callback(var_name, index, mode, key, v)
            )

            row = (i + 1) // 4 + 1
            column = (i + 1) % 4
            ttk.Checkbutton(main_frame, text=display_name, variable=var).grid(row=row, column=column, padx=10, pady=5, sticky="W")

        # Buttons
        self.manual_run_button = ttk.Button(
            main_frame, text="Manual Run", command=self.manual_run
        )
        self.manual_run_button.grid(row=row + 1, column=0, padx=10, pady=(10, 0), sticky="W")

        self.cancel_tasks_button = ttk.Button(
            main_frame, text="Cancel Tasks", command=self.cancel_tasks
        )
        self.cancel_tasks_button.grid(row=row + 1, column=1, padx=10, pady=(10, 0), sticky="W")

        self.quit_all_button = ttk.Button(
            main_frame, text="Quit All", command=self.quit_all
        )
        self.quit_all_button.grid(row=row + 1, column=2, padx=10, pady=(10, 0), sticky="W")

        # Log Text Box
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)

        self.log_text = tk.Text(
            logs_frame, wrap=tk.WORD, state="disabled", bg="#1E1E1E", fg="white"
        )
        self.log_text.grid(row=0, column=0, sticky="NSEW", padx=10, pady=10)

        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"))

        self.py_auto_raid.logger.addHandler(text_handler)
        self.py_auto_raid.logger.setLevel(logging.INFO)

    def checkbox_callback(self, var_name, index, mode, config_key, var):
        self.py_auto_raid.logger.info(f"Task {config_key.value} updated to {var.get()}.")
        # Update the config file when the checkbox state changes
        self.config_handler.update_setting("Settings", config_key.value, str(bool(var.get())))

    def manual_run(self):
        self.py_auto_raid.logger.info("Manual Run Triggered.")
        self.root.update_idletasks()
        threading.Thread(target=self._run_tasks, daemon=True).start()

    def cancel_tasks(self):
        self.py_auto_raid.logger.info("Tasks Cancelled.")

    def quit_all(self):
        self.py_auto_raid.logger.info("Quitting Application.")
        self.root.quit()

    def toggle_automated_mode(self):
        self.py_auto_raid.logger.info(f"Automated mode set to {self.automated_mode.get()}.")
        self.config_handler.update_setting("Settings", "automated_mode", str(bool(self.automated_mode.get())))

    def _run_tasks(self):
        for command_key, var in self.checkbox_vars.items():
            if var.get():
                self.py_auto_raid.logger.info(f"Running task: {command_key}")
                self.root.update_idletasks()
                self.py_auto_raid.run_task(command_key)
