import sys
import threading
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QSpinBox,
    QTextEdit, QFileDialog, QStatusBar,
)
from PySide6.QtGui import QFont
from PySide6.QtCore import QObject, Signal

from engine.pitch_detection import detect_notes
from engine.fretboard_mapping import map_to_fretboard
from engine.tab_renderer import render_tab


class Worker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, audio_path, bpm):
        super().__init__()
        self.audio_path = audio_path
        self.bpm = bpm

    def run(self):
        try:
            notes = detect_notes(self.audio_path)
            mapped = map_to_fretboard(notes)
            tab = render_tab(mapped, bpm=self.bpm)
            self.finished.emit(tab)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bassova")
        self.setMinimumSize(800, 500)
        self.audio_path = None

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        controls = QHBoxLayout()

        self.open_btn = QPushButton("Open audio file")
        self.open_btn.clicked.connect(self.open_file)
        controls.addWidget(self.open_btn)

        self.file_label = QLabel("No file selected")
        controls.addWidget(self.file_label, stretch=1)

        controls.addWidget(QLabel("BPM:"))
        self.bpm_spin = QSpinBox()
        self.bpm_spin.setRange(40, 300)
        self.bpm_spin.setValue(120)
        controls.addWidget(self.bpm_spin)

        self.generate_btn = QPushButton("Generate tab")
        self.generate_btn.setEnabled(False)
        self.generate_btn.clicked.connect(self.generate)
        controls.addWidget(self.generate_btn)

        layout.addLayout(controls)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Courier New", 11))
        self.output.setPlaceholderText("Tab will appear here after you open a file and click Generate tab.")
        layout.addWidget(self.output)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open audio file", "", "Audio files (*.wav *.mp3 *.flac *.ogg)"
        )
        if path:
            self.audio_path = path
            self.file_label.setText(Path(path).name)
            self.generate_btn.setEnabled(True)
            self.status.showMessage("File loaded. Set BPM and click Generate tab.")

    def generate(self):
        if not self.audio_path:
            return

        self.generate_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.output.setPlainText("")
        self.status.showMessage("Analyzing...")

        worker = Worker(self.audio_path, self.bpm_spin.value())
        worker.finished.connect(self.on_done)
        worker.error.connect(self.on_error)

        thread = threading.Thread(target=worker.run, daemon=True)
        thread.start()

    def on_done(self, tab):
        self.output.setPlainText(tab)
        self.generate_btn.setEnabled(True)
        self.open_btn.setEnabled(True)
        self.status.showMessage("Done.")

    def on_error(self, message):
        self.output.setPlainText(f"Error: {message}")
        self.generate_btn.setEnabled(True)
        self.open_btn.setEnabled(True)
        self.status.showMessage("Error during analysis.")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
