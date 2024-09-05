import ctypes
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
        self.ensure_topmost_timer = QTimer(self)
        self.ensure_topmost_timer.timeout.connect(self.ensure_topmost)
        self.ensure_topmost_timer.start(1000)  # Check every second
        
    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        layout = QVBoxLayout()
        self.time_label = QLabel('00:00:00')
        self.update_label_style()
        layout.addWidget(self.time_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
        
    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.setInterval(1000)
        
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
        font = QFont(self.config.get('font', 'Courier'), self.config.get('font_size', 48), QFont.Weight.Bold)
        self.time_label.setFont(font)
        self.time_label.setStyleSheet(f"""
            color: {self.config['color']};
            background-color: rgba(0, 0, 0, 100);
            border-radius: 10px;
            padding: 0px;
        """)
        
    def update_position(self):
        self.adjustSize()
        screen_index = self.config.get('screen_index', 0)
        if screen_index < len(self.screens):
            screen = self.screens[screen_index].availableGeometry()
        else:
            screen = self.screen().availableGeometry()
        
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
        painter.setBrush(QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        super().paintEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.update_position)

    def nativeEvent(self, eventType, message):
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            if msg.message == 274:  # WM_SYSCOMMAND
                if msg.wParam == 61728:  # SC_MINIMIZE
                    ctypes.windll.user32.ShowWindow(msg.hWnd, 1)  # SW_SHOWNORMAL
                    return True, 0
        return super().nativeEvent(eventType, message)

    def ensure_topmost(self):
        # Use Windows API to set the window as topmost
        if hasattr(ctypes.windll.user32, 'SetWindowPos'):
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            ctypes.windll.user32.SetWindowPos(
                int(self.winId()),
                HWND_TOPMOST,
                0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE
            )
        self.raise_()
        self.update_position()