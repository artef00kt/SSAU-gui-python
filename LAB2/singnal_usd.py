from PyQt5.QtCore import QObject, pyqtSignal

class SignalUSD(QObject):
    usd_changed = pyqtSignal(float)