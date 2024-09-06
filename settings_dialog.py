from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QComboBox, QWidget, QMessageBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeySequence, QIcon
import copy
from utils import resource_path

class SettingsDialog(QDialog):
    config_updated = Signal(dict)
    hotkeys_disabled = Signal()
    hotkeys_enabled = Signal()
    
    # Initialize dialog with current config and available screens
    def __init__(self, config, screens):
        super().__init__()
        self.original_config = config
        self.temp_config = copy.deepcopy(config)
        self.screens = screens
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.current_key_binding = None
        self.init_ui()
        
        # Connect the finished signal to re-enable hotkeys
        self.finished.connect(self.on_dialog_finished)
    
    # Create UI elements for all configurable options
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Start key binding
        self.start_key_button = QPushButton(self.temp_config['start_key'])
        self.start_key_button.setObjectName('start_key')
        self.start_key_button.clicked.connect(lambda: self.set_key_binding('start_key'))
        start_layout = self.create_option_layout('Start Key:', self.start_key_button)
        layout.addLayout(start_layout)
        
        # Stop key binding
        self.stop_key_button = QPushButton(self.temp_config['stop_key'])
        self.stop_key_button.setObjectName('stop_key')
        self.stop_key_button.clicked.connect(lambda: self.set_key_binding('stop_key'))
        stop_layout = self.create_option_layout('Stop Key:', self.stop_key_button)
        layout.addLayout(stop_layout)
        
        # Kill key binding
        self.kill_key_button = QPushButton(self.temp_config.get('kill_key', 'Not Set'))
        self.kill_key_button.setObjectName('kill_key')
        self.kill_key_button.clicked.connect(lambda: self.set_key_binding('kill_key'))
        kill_layout = self.create_option_layout('Kill Key:', self.kill_key_button)
        layout.addLayout(kill_layout)
        
        # Color picker
        self.color_combo = QComboBox()
        colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'white']
        self.color_combo.addItems(colors)
        self.color_combo.setCurrentText(self.temp_config['color'])
        self.color_combo.currentTextChanged.connect(self.update_color)
        color_layout = self.create_option_layout('Color:', self.color_combo)
        layout.addLayout(color_layout)
        
        # Position
        self.position_combo = QComboBox()
        self.position_combo.addItems(['top_left', 'top_right', 'bottom_left', 'bottom_right'])
        self.position_combo.setCurrentText(self.temp_config['position'])
        self.position_combo.currentTextChanged.connect(self.update_position)
        position_layout = self.create_option_layout('Position:', self.position_combo)
        layout.addLayout(position_layout)
        
        # Screen selection
        self.screen_combo = QComboBox()
        self.screen_combo.addItems([f"Screen {i+1}" for i in range(len(self.screens))])
        self.screen_combo.setCurrentIndex(self.temp_config.get('screen_index', 0))
        self.screen_combo.currentIndexChanged.connect(self.update_screen)
        screen_layout = self.create_option_layout('Screen:', self.screen_combo)
        layout.addLayout(screen_layout)
        
        # Save and Cancel buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_config)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    # Helper method to create consistent layout for options    
    def create_option_layout(self, label_text, widget):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(80)
        layout.addWidget(label)
        
        widget.setFixedWidth(120)
        layout.addWidget(widget)
        layout.addStretch()
        return layout

    # Prepare UI for capturing a new key binding    
    def set_key_binding(self, key_type):
        self.current_key_binding = key_type
        button = self.findChild(QPushButton, key_type)
        if button:
            button.setText('Press a key...')
            button.setFocus()
            self.grabKeyboard()  # Grab keyboard focus
        
    # Handle key press events for hotkey configuration
    def keyPressEvent(self, event):
        if self.current_key_binding:
            key = QKeySequence(event.key()).toString()
            
            # Check if the key is already in use
            if self.is_key_duplicate(key):
                QMessageBox.warning(self, "Duplicate Key", f"The key '{key}' is already in use. Please choose a different key.")
                self.reset_key_binding()
                return
            
            button = self.findChild(QPushButton, self.current_key_binding)
            if button:
                button.setText(key)
                self.temp_config[self.current_key_binding] = key
            
            self.reset_key_binding()
            self.config_updated.emit(self.temp_config)
        else:
            super().keyPressEvent(event)
    
    # Reset UI after key binding is set or cancelled
    def reset_key_binding(self):
        self.releaseKeyboard()
        self.current_key_binding = None
        for button in [self.start_key_button, self.stop_key_button, self.kill_key_button]:
            if button.text() == 'Press a key...':
                button.setText(self.temp_config.get(button.objectName(), 'Not Set'))
    
    # Check if the key is already in use
    def is_key_duplicate(self, key):
        return key in [self.temp_config['start_key'], self.temp_config['stop_key'], self.temp_config.get('kill_key')]
        
    def update_color(self, color):
        self.temp_config['color'] = color
        self.config_updated.emit(self.temp_config)
        
    def update_position(self, position):
        self.temp_config['position'] = position
        self.config_updated.emit(self.temp_config)
        
    def update_screen(self, index):
        self.temp_config['screen_index'] = index
        self.config_updated.emit(self.temp_config)
        
    def save_config(self):
        self.original_config.update(self.temp_config)
        self.accept()
        
    # Revert changes if dialog is cancelled
    def reject(self):
        # Revert changes
        self.temp_config = copy.deepcopy(self.original_config)
        self.config_updated.emit(self.original_config)
        super().reject()

    # Reset temp_config to original_config each time the dialog is shown
    def showEvent(self, event):
        self.temp_config = copy.deepcopy(self.original_config)
        self.start_key_button.setText(self.temp_config['start_key'])
        self.stop_key_button.setText(self.temp_config['stop_key'])
        self.kill_key_button.setText(self.temp_config.get('kill_key', 'Not Set'))
        self.color_combo.setCurrentText(self.temp_config['color'])
        self.position_combo.setCurrentText(self.temp_config['position'])
        self.screen_combo.setCurrentIndex(self.temp_config.get('screen_index', 0))
        self.hotkeys_disabled.emit()  # Disable hotkeys when settings dialog is shown
        super().showEvent(event)
    
    # Re-enable hotkeys when dialog is closed
    def on_dialog_finished(self):
        self.hotkeys_enabled.emit()  # Re-enable hotkeys when settings dialog is closed