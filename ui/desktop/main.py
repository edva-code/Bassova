import sys
import threading
import time
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
from engine.audio_input import detect_bpm


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

class BpmWorker(QObject):
    finished = Signal(int)

    def __init__(self, audio_path):
        super().__init__()
        self.audio_path = audio_path

    def run(self):
        try:
            bpm = detect_bpm(self.audio_path)
            self.finished.emit(bpm)
        except Exception:
            self.finished.emit(120)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bassova")
        self.setMinimumSize(800, 500)
        self.audio_path = None
        self._bpm_worker = None
        self._analysis_worker = None

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

        self.tap_btn = QPushButton("Tap")
        self.tap_btn.clicked.connect(self.tap_tempo)
        controls.addWidget(self.tap_btn)

        self.generate_btn = QPushButton("Generate tab")
        self.generate_btn.setEnabled(False)
        self.generate_btn.clicked.connect(self.generate)
        controls.addWidget(self.generate_btn)

        self._taps = []
        layout.addLayout(controls)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.output.setFont(QFont("Courier New", 11))
        self.output.setPlaceholderText("Tab will appear here after you open a file and click Generate tab.")
        layout.addWidget(self.output)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open audio file",
            "",
            "Audio files (*.wav *.mp3 *.flac *.ogg)",
        )
        if path:
            self.audio_path = path
            self.file_label.setText(Path(path).name)
            self.generate_btn.setEnabled(False)
            self.status.showMessage("Detecting BPM...")

            self._bpm_worker = BpmWorker(path)
            self._bpm_worker.finished.connect(self.on_bpm_detected)
            thread = threading.Thread(target=self._bpm_worker.run, daemon=True)
            thread.start()

    def on_bpm_detected(self, bpm):
        self.bpm_spin.setValue(bpm)
        self.generate_btn.setEnabled(True)
        self.status.showMessage(f"Detected BPM: {bpm}. Click Generate tab.")


    def tap_tempo(self):
        now = time.time()
        if self._taps and now - self._taps[-1] > 3.0:
            self._taps.clear()
        self._taps.append(now)
        if len(self._taps) >= 2:
            intervals = [self._taps[i + 1] - self._taps[i] for i in range(len(self._taps) - 1)]
            bpm = round(60 / (sum(intervals) / len(intervals)))
            self.bpm_spin.setValue(bpm)
            self.status.showMessage(f"Tap tempo: {bpm} BPM ({len(self._taps)} taps)")

    def generate(self):
        if not self.audio_path:
            return

        self.generate_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.output.setPlainText("")
        self.status.showMessage("Analyzing...")

        self._analysis_worker = Worker(self.audio_path, self.bpm_spin.value())
        self._analysis_worker.finished.connect(self.on_done)
        self._analysis_worker.error.connect(self.on_error)

        thread = threading.Thread(target=self._analysis_worker.run, daemon=True)
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
