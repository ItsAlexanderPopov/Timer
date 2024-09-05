from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QLabel, QComboBox, QWidget)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QKeySequence, QIcon
import copy
from utils import resource_path

class SettingsDialog(QDialog):
    config_updated = Signal(dict)
    
    def __init__(self, config, screens):
        super().__init__()
        self.original_config = config
        self.temp_config = copy.deepcopy(config)
        self.screens = screens
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Start key binding
        start_layout = self.create_option_layout('Start Key:', self.temp_config['start_key'], self.set_key_binding, 'start_key')
        layout.addLayout(start_layout)
        
        # Stop key binding
        stop_layout = self.create_option_layout('Stop Key:', self.temp_config['stop_key'], self.set_key_binding, 'stop_key')
        layout.addLayout(stop_layout)
        
        # Simplified Color picker
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
        
    def create_option_layout(self, label_text, widget, *args):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFixedWidth(80)  # Set a fixed width for all labels
        layout.addWidget(label)
        
        if isinstance(widget, str):
            widget = QPushButton(widget)
            widget.clicked.connect(lambda: args[0](*args[1:]))
        
        widget.setFixedWidth(120)  # Set a fixed width for all widgets
        layout.addWidget(widget)
        layout.addStretch()  # Add stretch to push widgets to the left
        return layout
        
    def set_key_binding(self, key_type):
        button = self.findChild(QPushButton, key_type)
        if button:
            button.setText('Press a key...')
            button.setFocus()
            button.keyPressEvent = lambda e: self.on_key_press(e, key_type, button)
        
    def on_key_press(self, event, key_type, button):
        key = QKeySequence(event.key()).toString()
        button.setText(key)
        self.temp_config[key_type] = key
        button.keyPressEvent = QPushButton.keyPressEvent
        self.config_updated.emit(self.temp_config)
        
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
        
    def reject(self):
        self.config_updated.emit(self.original_config)
        super().reject()
        
    def showEvent(self, event):
        # Reset temp_config to original_config each time the dialog is shown
        self.temp_config = copy.deepcopy(self.original_config)
        self.findChild(QPushButton, 'start_key').setText(self.temp_config['start_key'])
        self.findChild(QPushButton, 'stop_key').setText(self.temp_config['stop_key'])
        self.color_combo.setCurrentText(self.temp_config['color'])
        self.position_combo.setCurrentText(self.temp_config['position'])
        self.screen_combo.setCurrentIndex(self.temp_config.get('screen_index', 0))
        super().showEvent(event)