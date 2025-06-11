import sys
import threading
import pygame
import os

from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout,
    QVBoxLayout, QHBoxLayout, QCheckBox, QShortcut
)
from PyQt5.QtGui import QKeySequence, QFont

pygame.mixer.init()
pygame.mixer.set_num_channels(20)

SOUNDS_FOLDER = 'sounds/notes'

def get_wav_files(folder=SOUNDS_FOLDER):
    return sorted([f for f in os.listdir(folder) if f.lower().endswith(".wav")])


class SoundButton(QPushButton):
    def __init__(self, sound_path, shortcut_key, channel_index, base_color, parent=None):
        super().__init__(parent)
        self.app_font = 'Segoe UI'
        self.font_size = 14

        self.sound = pygame.mixer.Sound(sound_path)
        length_seconds = int(self.sound.get_length())
        minutes = length_seconds // 60
        seconds = length_seconds % 60
        self.sound_duration_str = f"{minutes:02}:{seconds:02}"

        self.channel = pygame.mixer.Channel(channel_index)
        self.shortcut_key = shortcut_key
        self.filename = os.path.splitext(os.path.basename(sound_path))[0]
        self.setCheckable(True)
        self.clicked.connect(self.on_click)
        self.loop_mode = False
        self.base_color = base_color

        self.setFont(QFont(self.app_font, self.font_size))
        self.setMinimumSize(180, 180)

        self.default_style = f"""
            QPushButton {{
                background-color: {self.base_color};
                border-radius: 18px;
                font-weight: bold;
                color: white;
            }}
            QPushButton:hover {{
                background-color: #444;
            }}
        """
        self.setStyleSheet(self.default_style)

        self.setText(f"{self.filename} ({self.shortcut_key})\n{self.sound_duration_str}")

        shortcut = QShortcut(QKeySequence(self.shortcut_key), self)
        shortcut.activated.connect(self.click)

    def on_click(self):
        if self.channel.get_busy():
            self.stop_sound()
        else:
            loop = self.parent().loop_toggle.isChecked()
            self.play_sound(loop)

    def play_sound(self, loop=False):
        def _play():
            loops = -1 if loop else 0
            self.channel.play(self.sound, loops=loops)
            self.setChecked(True)
            self.update_active_state(True)
            while self.channel.get_busy():
                pygame.time.wait(100)
            self.setChecked(False)
            self.update_active_state(False)

        threading.Thread(target=_play).start()

    def stop_sound(self):
        self.channel.stop()
        self.setChecked(False)
        self.update_active_state(False)

    def update_active_state(self, is_active):
        if is_active:
            self.setFont(QFont(self.app_font, self.font_size, QFont.Bold))
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.base_color};
                    border: 3px solid white;
                    border-radius: 18px;
                    font-weight: bold;
                    color: white;
                }}
            """)
        else:
            self.setFont(QFont(self.app_font, self.font_size))
            self.setStyleSheet(self.default_style)


class SoundLooper(QWidget):
    def __init__(self, grid_rows=3, grid_cols=3):
        super().__init__()
        self.app_font = 'Segoe UI'
        self.font_size = 20
        self.setWindowTitle("🎛️ PyQt5 Sound Looper")
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QCheckBox {
            }
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
                border-radius: 10px;
                background-color: #777;
                border: 1px solid #555;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
            }
        """)

        self.layout = QVBoxLayout()
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)
        self.setLayout(self.layout)

        self.buttons = []
        self.load_buttons(grid_rows, grid_cols)

        # Bottom controls
        self.controls_layout = QHBoxLayout()
        self.loop_toggle = QCheckBox("Loop mode")
        self.loop_toggle.setFont(QFont(self.app_font, self.font_size))
        self.loop_toggle.setStyleSheet("""
                    QCheckBox {
                        padding: 10px;
                        font-weight: bold;
                        color: white;
                    }
                """)
        self.controls_layout.addWidget(self.loop_toggle)

        self.stop_all_btn = QPushButton("🛑 Stop All Sounds")
        self.stop_all_btn.setFont(QFont(self.app_font, self.font_size))
        self.stop_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        self.stop_all_btn.clicked.connect(self.stop_all_sounds)
        self.controls_layout.addWidget(self.stop_all_btn)

        self.layout.addLayout(self.controls_layout)

    def load_buttons(self, rows, cols):
        files = get_wav_files()
        keys = [
            '1', '2', '3', '4', '5',
            'Q', 'W', 'E', 'R', 'T',
            'A', 'S', 'D', 'F', 'G',
            'Z', 'X', 'C', 'V', 'B',
        ]

        color_palette = [
            "#FF6B6B",  # Coral Red
            "#F06595",  # Hot Pink
            "#CC5DE8",  # Light Purple
            "#845EF7",  # Violet
            "#5C7CFA",  # Indigo Blue
            "#339AF0",  # Sky Blue
            "#22B8CF",  # Cyan
            "#20C997",  # Teal Green
            "#51CF66",  # Light Green
            "#94D82D",  # Lime
            "#FCC419",  # Yellow
            "#FF922B",  # Orange
            "#FF6B00",  # Deep Orange
            "#E64980",  # Deep Pink
            "#BE4BDB",  # Rich Purple
            "#7950F2",  # Electric Violet
            "#4C6EF5",  # Royal Blue
            "#228BE6",  # Blue
            "#15AABF",  # Light Cyan
            "#12B886",  # Emerald
            "#40C057",  # Soft Green
            "#82C91E",  # Chartreuse
            "#FAB005",  # Goldenrod
            "#F76707",  # Burnt Orange
            "#C2255C",  # Ruby Red
        ]

        max_buttons = min(len(files), rows * cols, len(keys), len(color_palette))

        for index in range(max_buttons):
            row, col = divmod(index, cols)
            sound_path = os.path.join(SOUNDS_FOLDER, files[index])
            btn = SoundButton(sound_path, keys[index], index, color_palette[index], self)
            self.grid.addWidget(btn, row, col)
            self.buttons.append(btn)

    def stop_all_sounds(self):
        for btn in self.buttons:
            btn.stop_sound()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    looper = SoundLooper(grid_rows=5, grid_cols=5)
    looper.resize(1500, 400)

    # Center the window on the screen
    screen = app.primaryScreen()
    screen_geometry = screen.availableGeometry()
    x = (screen_geometry.width() - looper.width()) // 2
    y = (screen_geometry.height() - looper.height()) // 2 - 220
    looper.move(x, y)

    looper.show()
    sys.exit(app.exec_())
