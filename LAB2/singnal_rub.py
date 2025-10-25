from PyQt5.QtCore import QObject, pyqtSignal

class SignalRUB(QObject):
    rub_changed = pyqtSignal(float)