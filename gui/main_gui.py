import customtkinter as ctk
from app.pyAutoRaid import PyAutoRaid
from utils.config_handler import ConfigHandler
from utils.text_handler import TextHandler
import threading
import logging

class MainGUI:
    def __init__(self, root: ctk.CTk, py_auto_raid_instance: PyAutoRaid):
        self.py_auto_raid = py_auto_raid_instance
        self.config_handler = ConfigHandler()
        self.root = root
        self.root.title("PyAutoRaid Task Selector")

        # Set appearance mode and configure grid
        ctk.set_appearance_mode("dark")  # "dark" or "light"
        ctk.set_default_color_theme("blue")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Create main frame for controls
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")

        # Create logs frame
        logs_frame = ctk.CTkFrame(self.root)
        logs_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Automated Mode Checkbox
        self.automated_mode = ctk.BooleanVar(value=self.config_handler.read_setting("Settings", "automated_mode").lower() == "true")
        automated_mode_label = ctk.CTkLabel(main_frame, text="Automated Mode")
        automated_mode_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.automated_mode_checkbox = ctk.CTkCheckBox(
            main_frame, text="Enable", variable=self.automated_mode, command=self.toggle_automated_mode
        )
        self.automated_mode_checkbox.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="w")

        # Dynamically create task checkboxes
        self.checkbox_vars = {}
        for i, (command_key, display_name) in enumerate(self.py_auto_raid.command_factory.get_display_names()):
            initial_value = self.config_handler.read_setting("Settings", command_key.value) == "True"
            var = ctk.BooleanVar(value=initial_value)
            self.checkbox_vars[command_key] = var

            ctk.CTkCheckBox(
                main_frame, text=display_name, variable=var, 
                command=lambda key=command_key, v=var: self.checkbox_callback(key, v)
            ).grid(row=(i // 4) + 1, column=i % 4, padx=10, pady=5, sticky="w")

        # Buttons
        self.manual_run_button = ctk.CTkButton(
            main_frame, text="Manual Run", command=self.manual_run
        )
        self.manual_run_button.grid(row=(len(self.checkbox_vars) // 4) + 2, column=0, padx=10, pady=(10, 0), sticky="w")

        self.quit_all_button = ctk.CTkButton(
            main_frame, text="Quit All", command=self.quit_all
        )
        self.quit_all_button.grid(row=(len(self.checkbox_vars) // 4) + 2, column=2, padx=10, pady=(10, 0), sticky="w")

        # Log Text Box
        logs_frame.grid_columnconfigure(0, weight=1)
        logs_frame.grid_rowconfigure(0, weight=1)
        
        self.log_text = ctk.CTkTextbox(
            logs_frame, wrap="word", state="disabled", width=400, height=200
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"))

        self.py_auto_raid.logger.addHandler(text_handler)
        self.py_auto_raid.logger.setLevel(logging.INFO)
        
        self.root.bind("<F5>", lambda event: self.close_app())


    def checkbox_callback(self, config_key, var):
        self.py_auto_raid.logger.info(f"Task {config_key.value} updated to {var.get()}.")
        self.config_handler.update_setting("Settings", config_key.value, str(var.get()))

    def manual_run(self):
        self.py_auto_raid.logger.info("Manual Run Triggered.")
        threading.Thread(target=self._run_tasks, daemon=True).start()

    def quit_all(self):
        self.py_auto_raid.logger.info("Quitting Application.")
        self.root.quit()
        
    def close_app(self):
        """Close the application."""
        self.py_auto_raid.logger.info("Application closed by F5 key.")
        self.root.quit()

    def toggle_automated_mode(self):
        self.py_auto_raid.logger.info(f"Automated mode set to {self.automated_mode.get()}.")
        self.config_handler.update_setting("Settings", "automated_mode", str(self.automated_mode.get()))

    def _run_tasks(self):
        for command_key, var in self.checkbox_vars.items():
            if var.get():
                self.py_auto_raid.logger.info(f"Running task: {command_key}")
                self.py_auto_raid.run_task(command_key)

        self.py_auto_raid.click_handler.back_to_bastion()
