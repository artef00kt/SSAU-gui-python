from PyQt5.QtCore import QObject, pyqtSignal

class SignalEUR(QObject):
    eur_changed = pyqtSignal(float)