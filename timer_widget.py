from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtGui import QColor, QPainter, QFont

class TimerWidget(QWidget):
    def __init__(self, config, screens):
        super().__init__()
        self.config = config
        self.screens = screens
        self.init_ui()
        self.setup_timer()
        self.time = QTime(0, 0)
        self.timer_running = False
        
    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        self.time_label = QLabel('00:00:00')
        self.update_label_style()
        layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
        
    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.setInterval(1000)  # Update every second
        
    def update_time(self):
        self.time = self.time.addSecs(1)
        self.time_label.setText(self.time.toString('hh:mm:ss'))
        
    def start_timer(self):
        if not self.timer_running:
            self.time.setHMS(0, 0, 0)
            self.timer.start()
            self.timer_running = True
            self.time_label.setText('00:00:00')
        
    def stop_timer(self):
        if self.timer_running:
            self.timer.stop()
            self.timer_running = False
        
    def update_config(self, new_config):
        self.config = new_config
        self.update_label_style()
        self.update_position()
        
    def update_label_style(self):
        font = QFont("Courier", 48, QFont.Weight.Bold)
        self.time_label.setFont(font)
        self.time_label.setStyleSheet(f"color: {self.config['color']};")
        
    def update_position(self):
        self.adjustSize()  # Ensure the widget size is updated
        screen_index = self.config.get('screen_index', 0)
        if screen_index < len(self.screens):
            screen = self.screens[screen_index].availableGeometry()
        else:
            screen = self.screen().availableGeometry()  # Fallback to primary screen
        
        position = self.config['position']
        
        if position == 'top_left':
            self.move(screen.left(), screen.top())
        elif position == 'top_right':
            self.move(screen.right() - self.width(), screen.top())
        elif position == 'bottom_left':
            self.move(screen.left(), screen.bottom() - self.height())
        elif position == 'bottom_right':
            self.move(screen.right() - self.width(), screen.bottom() - self.height())
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(0, 0, 0, 0))  # Transparent background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        super().paintEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.update_position)  # Ensure correct position when shown