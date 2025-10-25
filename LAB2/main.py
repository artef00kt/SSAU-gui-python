import sys
import os
import json
from dotenv import load_dotenv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from singnal_eur import SignalEUR
from singnal_rub import SignalRUB
from singnal_usd import SignalUSD

currencies = [
    {'code': 'RUB'},
    {'code': 'USD'},
    {'code': 'EUR'},
]

class CurrencyConverter(QMainWindow):
    def __init__(self, signal_eur, signal_rub, signal_usd):
        super().__init__()

        self.signals = {
            'EUR': signal_eur,
            'RUB': signal_rub,
            'USD': signal_usd,
        }
        self.updating = False
        self.api_key = os.getenv('API_KEY')
        self.network_manager = QNetworkAccessManager()

        url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/latest/USD"
        request = QNetworkRequest(QUrl(url))
        self.network_manager.get(request)
        self.network_manager.finished.connect(self.setupRates)

        self.setWindowTitle("Конвертер валют")
        self.setFixedSize(400, 330)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 20, 40, 40)
        
        title = QLabel("Конвертер валют")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 26px; 
                font-weight: bold; 
                color: #2c3e50; 
                padding: 10px;
            }
        """)
        main_layout.addWidget(title)
        
        self.createLayout(main_layout)

        self.initSignals()

    def setupRates(self, response):
        error = response.error()
        if error == response.NoError:
            data = json.loads(response.readAll().data())
            conversion_rates = data.get('conversion_rates', {})

            self.rates = {
                'USD': conversion_rates.get('USD', 1),
                'RUB': conversion_rates.get('RUB', 1),
                'EUR': conversion_rates.get('EUR', 1),
            }

        print(self.rates)

        
    def createLayout(self, parent_layout):
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        grid_layout = QGridLayout(container)
        grid_layout.setVerticalSpacing(20)
        grid_layout.setHorizontalSpacing(15)
        
        self.fields = {}
        
        for i, currency in enumerate(currencies, 1):
            text_label = QLabel(f"{currency['code']}")
            text_label.setStyleSheet("font-size: 14px; color: #2c3e50; padding: 10px")

            input_field = QLineEdit()
            input_field.setValidator(QDoubleValidator(0.0, 100000000.0, 4))
            input_field.setAlignment(Qt.AlignRight)
            input_field.setMinimumHeight(30)
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #bdc3c7;
                    border-radius: 4px;
                    
                    font-size: 16px;
                    background-color: #f8f9fa;
                    selection-background-color: #3498db;
                    min-width: 10px;
                }
                QLineEdit:focus {
                    background-color: #ffffff;
                }
            """)
            
            self.fields[currency['code']] = input_field
            setattr(self, f"{currency['code'].lower()}_field", input_field)
            
            grid_layout.addWidget(text_label, i, 1)
            grid_layout.addWidget(input_field, i, 0)
        
        parent_layout.addWidget(container)
    
    def initSignals(self):
        self.signals['USD'].usd_changed.connect(self.updateEurRub)
        self.signals['EUR'].eur_changed.connect(self.updateUsdRub)
        self.signals['RUB'].rub_changed.connect(self.updateUsdEur)

        self.fields['USD'].textChanged.connect(self.onUsdChanged)
        self.fields['EUR'].textChanged.connect(self.onEurChanged)
        self.fields['RUB'].textChanged.connect(self.onRubChanged)

    def onUsdChanged(self, text):
        if self.updating or not self.rates:
            return
        try:
            value = float(text)
        except ValueError:
            return
        self.signals['USD'].usd_changed.emit(value)

    def onEurChanged(self, text):
        if self.updating or not self.rates:
            return
        try:
            value = float(text)
        except ValueError:
            return
        self.signals['EUR'].eur_changed.emit(value)

    def onRubChanged(self, text):
        if self.updating or not self.rates:
            return
        try:
            value = float(text)
        except ValueError:
            return
        self.signals['RUB'].rub_changed.emit(value)

    def updateEurRub(self, usd_value):
        if self.updating or not self.rates:
            return
        self.updating = True
        eur = usd_value * self.rates['EUR']
        rub = usd_value * self.rates['RUB']
        self.fields['EUR'].setText(f"{eur:.3f}")
        self.fields['RUB'].setText(f"{rub:.3f}")
        self.updating = False

    def updateUsdRub(self, eur_value):
        if self.updating or not self.rates:
            return
        self.updating = True
        usd = eur_value / self.rates['EUR']
        rub = eur_value / self.rates['EUR'] * self.rates['RUB']
        self.fields['USD'].setText(f"{usd:.3f}")
        self.fields['RUB'].setText(f"{rub:.3f}")
        self.updating = False

    def updateUsdEur(self, rub_value):
        if self.updating or not self.rates:
            return
        self.updating = True
        usd = rub_value / self.rates['RUB']
        eur = rub_value / self.rates['RUB'] * self.rates['EUR']
        self.fields['USD'].setText(f"{usd:.3f}")
        self.fields['EUR'].setText(f"{eur:.3f}")
        self.updating = False

if __name__ == "__main__":
    load_dotenv()

    app = QApplication(sys.argv)

    signal_eur = SignalEUR()
    signal_rub = SignalRUB()
    signal_usd = SignalUSD()
    
    window = CurrencyConverter(signal_eur, signal_rub, signal_usd)
    window.show()
    
    sys.exit(app.exec_())