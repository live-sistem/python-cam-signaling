import os
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QWidget, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
from datetime import datetime

class MotionDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Motion Detector")
        self.setGeometry(100, 100, 400, 300)
        
        # Настройки
        self.save_path = os.path.join(os.getcwd(), "recordings")
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        
        self.is_recording = False
        self.motion_detected = False
        self.record_timer = None
        self.cap = None
        self.out = None
        self.frames_to_record = 0
        self.prev_frame = None
        
        # Инициализация UI
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Статус: Ожидание запуска")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.start_button = QPushButton("Запустить")
        self.start_button.clicked.connect(self.toggle_detection)
        layout.addWidget(self.start_button)
        
        self.change_path_button = QPushButton("Изменить путь сохранения")
        self.change_path_button.clicked.connect(self.change_save_path)
        layout.addWidget(self.change_path_button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
    def toggle_detection(self):
        if not self.is_recording:
            self.start_detection()
            self.start_button.setText("Остановить")
        else:
            self.stop_detection()
            self.start_button.setText("Запустить")
    
    def start_detection(self):
        self.is_recording = True
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Ошибка", "Не удалось открыть камеру!")
            return
        
        self.status_label.setText("Статус: Наблюдаю")
        
        # Таймер для обработки кадров
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_motion)
        self.timer.start(100)  # Проверка каждые 100 мс
    
    def stop_detection(self):
        self.is_recording = False
        if self.timer:
            self.timer.stop()
        if self.cap:
            self.cap.release()
        if self.out:
            self.out.release()
        self.status_label.setText("Статус: Остановлено")
    
    def check_motion(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return
        
        frame_diff = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = any(cv2.contourArea(c) > 500 for c in contours)
        
        if motion_detected:
            if not self.motion_detected:
                self.start_recording()
            self.motion_detected = True
            self.frames_to_record = 100  # 10 сек при 10 FPS
        
        if self.motion_detected:
            if self.frames_to_record > 0:
                self.frames_to_record -= 1
                if self.out:
                    self.out.write(frame)
            else:
                self.stop_recording()
                self.motion_detected = False
        
        self.prev_frame = gray
    
    def start_recording(self):
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.save_path, f"recording_{now}.avi")
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        fps = 10.0
        frame_size = (640, 480)  # Подстрой под разрешение своей камеры
        
        self.out = cv2.VideoWriter(filename, fourcc, fps, frame_size)
        self.status_label.setText("Статус: Запись видео...")
    
    def stop_recording(self):
        if self.out:
            self.out.release()
            self.out = None
        self.status_label.setText("Статус: Наблюдаю")
    
    def change_save_path(self):
        new_path = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        if new_path:
            self.save_path = new_path
            QMessageBox.information(self, "Успех", f"Путь сохранения изменён на: {new_path}")
    
    def closeEvent(self, event):
        self.stop_detection()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MotionDetectionApp()
    window.show()
    sys.exit(app.exec_())