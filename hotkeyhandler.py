from PySide6.QtCore import QObject, Signal
from multiprocessing import Process, Event
import os
import signal

def import_keyboard():
    global keyboard
    if 'keyboard' not in globals():
        import keyboard
    return keyboard

def kill_process(pid, exit_event, kill_key):
    keyboard = import_keyboard()
    while not exit_event.is_set():
        if keyboard.is_pressed(kill_key):
            os.kill(pid, signal.SIGTERM)
            exit_event.set()

class HotkeyHandler(QObject):
    start_signal = Signal()
    stop_signal = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.kill_process = None
        self.exit_event = Event()
        self.keyboard = import_keyboard()
        self.hotkeys_active = True
        self.setup_hotkeys()

    def setup_hotkeys(self):
        self.keyboard.add_hotkey(self.config['start_key'], self.emit_start)
        self.keyboard.add_hotkey(self.config['stop_key'], self.emit_stop)
        
        if 'kill_key' in self.config:
            self.kill_process = Process(target=kill_process, args=(os.getpid(), self.exit_event, self.config['kill_key']))
            self.kill_process.start()

    def emit_start(self):
        if self.hotkeys_active:
            self.start_signal.emit()

    def emit_stop(self):
        if self.hotkeys_active:
            self.stop_signal.emit()

    def update_config(self, new_config):
        self.config = new_config
        self.keyboard.unhook_all_hotkeys()
        if self.kill_process:
            self.exit_event.set()
            self.kill_process.join()
        self.exit_event.clear()
        self.setup_hotkeys()

    def disable_hotkeys(self):
        self.hotkeys_active = False

    def enable_hotkeys(self):
        self.hotkeys_active = True

    def __del__(self):
        if self.kill_process:
            self.exit_event.set()
            self.kill_process.join()