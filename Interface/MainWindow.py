import os

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget

from ModelFileManager import ModelFileManager
from GoogleCloudStorage import GoogleCloudStorage
from Interface.CalibrationTab import CalibrationTab
from Interface.CheatingDetectionTab import CheatingDetectionTab
from Interface.GazeDirectionTab import GazeDirectionTab
from Interface.SettingsTab import SettingsTab
from main import Camera, CheatingDetection, EyesDetector, EyesRecognizer


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Eye Tracker")
        self.screen_size = self.screen().size()
        self.setFixedSize(self.screen_size)
        self.initial_position = self.pos()

        self.camera = Camera(0)
        self.tab_using_camera = 0

        self.cloud_manager = GoogleCloudStorage()

        self.cheating_detection = CheatingDetection()
        self.calibration_taken = False
        self.eye_detector = EyesDetector()
        self.eyes_recognizer = EyesRecognizer()
        self.model_version = ''
        is_loaded, self.model_version, model_files = ModelFileManager.get_latest_model_if_exists()
        if is_loaded:
            self.eyes_recognizer.load_state(model_files['left'], model_files['right'])
        print(self.eyes_recognizer.is_loaded)

        self.tabs_list = [
            SettingsTab(self, "Settings"),
            CalibrationTab(self, "Calibration"),
            GazeDirectionTab(self, "Gaze Direction"),
            CheatingDetectionTab(self, "Cheating Detection")
        ]

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.currentChanged.connect(self.tab_changed)
        self.tabs.setDocumentMode(True)

        for tab in self.tabs_list:
            self.tabs.addTab(tab, tab.tab_name)

        self.setCentralWidget(self.tabs)

    def moveEvent(self, event):
        if event.pos() != self.initial_position:
            self.move(self.initial_position)

    def tab_changed(self, index: int) -> None:
        if self.camera.is_capturing():
            self.camera.stop_capture()
            if self.tab_using_camera == 2 or self.tab_using_camera == 3:
                self.tabs_list[self.tab_using_camera].timer.stop()

        self.tabs_list[index].tab_selected()
        self.tab_using_camera = index


app = QApplication([])
main_window = MainWindow()
main_window.showMaximized()
app.exec()