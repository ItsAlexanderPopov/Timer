import sys
import os
import tempfile
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer, QObject, Signal
from timer_widget import TimerWidget
from config_manager import ConfigManager
from utils import resource_path
from settings_dialog import SettingsDialog
import psutil
from hotkeyhandler import HotkeyHandler, import_keyboard

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SingleInstance:
    def __init__(self):
        self.lockfile = os.path.normpath(tempfile.gettempdir() + '/timer.lock')

    def already_running(self):
        try:
            if os.path.exists(self.lockfile):
                with open(self.lockfile, 'r') as f:
                    pid = int(f.read())
                if psutil.pid_exists(pid):
                    return True
            with open(self.lockfile, 'w') as f:
                f.write(str(os.getpid()))
            return False
        except:
            return False

class TimerApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.single_instance = SingleInstance()
        if self.single_instance.already_running():
            QMessageBox.warning(None, "Timer", "An instance of Timer is already running.")
            sys.exit(1)

        self.setApplicationName("Timer")
        self.setApplicationDisplayName("Timer")
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.screens = self.screens()
        self.timer_widget = None
        self.settings_dialog = None
        self.hotkey_handler = None
        self.tray_icon = None
        self.setQuitOnLastWindowClosed(False)
        
        # Set the application icon
        icon = QIcon(resource_path("icon.ico"))
        self.setWindowIcon(icon)
        
        QTimer.singleShot(0, self.delayed_init)

    def delayed_init(self):
        self.timer_widget = TimerWidget(self.config, self.screens)
        self.settings_dialog = SettingsDialog(self.config, self.screens)
        self.hotkey_handler = HotkeyHandler(self.config)
        self.hotkey_handler.start_signal.connect(self.timer_widget.start_timer)
        self.hotkey_handler.stop_signal.connect(self.timer_widget.stop_timer)
        self.settings_dialog.hotkeys_disabled.connect(self.hotkey_handler.disable_hotkeys)
        self.settings_dialog.hotkeys_enabled.connect(self.hotkey_handler.enable_hotkeys)
        self.settings_dialog.config_updated.connect(self.update_config_preview)
        self.setup_tray_icon()
        self.timer_widget.show()
        self.timer_widget.update_position()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = resource_path("icon.png")
        icon = QIcon(icon_path)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Timer")
        self.tray_menu = QMenu()
        self.settings_action = self.tray_menu.addAction("Settings")
        self.quit_action = self.tray_menu.addAction("Quit")
        self.settings_action.triggered.connect(self.show_settings)
        self.quit_action.triggered.connect(self.quit)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.show()

    def show_settings(self):
        if self.settings_dialog.exec() == SettingsDialog.Accepted:
            self.update_config(self.config)
            self.config_manager.save_config(self.config)
        else:
            # If dialog was cancelled, revert to original config
            self.update_config_preview(self.config)

    def update_config_preview(self, new_config):
        self.timer_widget.update_config(new_config)
        self.hotkey_handler.update_config(new_config)

    def update_config(self, new_config):
        self.config = new_config
        self.timer_widget.update_config(self.config)
        self.hotkey_handler.update_config(self.config)
    
    def quit(self):
        keyboard = import_keyboard()
        keyboard.unhook_all_hotkeys()
        self.tray_icon.setVisible(False)
        if os.path.exists(self.single_instance.lockfile):
            os.remove(self.single_instance.lockfile)
        super().quit()

if __name__ == '__main__':
    app = TimerApp(sys.argv)
    sys.exit(app.exec())