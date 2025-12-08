import sys
import os
from PyQt5.QtCore import QUrl, QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine
from datetime import *


class Interface(QObject):
    # Генерируем новый hashPrint при каждом сохранении
    hashPrint = hex(abs(hash(f'{datetime.now()}')))[2:]
    # Сигнал для сохранения canvas с передачей строкового параметра
    saveRequested = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        # Создаем таймер с интервалом 5 секунд (5000 мс)
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_timeout)
        self.timer.start(5000)  # Сохраняем каждые 5 секунд
        
        # Создаем директорию для сохранения, если её нет
        self.save_dir = "saved_canvas"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def on_timer_timeout(self):
        # Эмитируем сигнал для сохранения canvas с передачей строки
        self.saveRequested.emit(self.hashPrint) 


if __name__ == '__main__':

    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    interface = Interface()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("_backend", interface)

    # Загружаем QML
    engine.load("mainWindow.qml")

    # Проверка успешной загрузки QML
    if not engine.rootObjects():
        print("Ошибка: Не удалось загрузить QML файл!")
        sys.exit(-1)

    sys.exit(app.exec())
