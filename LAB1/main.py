import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QLinearGradient
from PyQt5.QtCore import Qt

TEXT_1 = 'Надпись 1'
TEXT_2 = 'Подпись 2'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Приложение на PyQT")
        self.setGeometry(100, 100, 800, 500)

        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2b2b2b, stop: 1 #3c3c3c);
                border-radius: 10px;
            }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        self.central_widget.setLayout(main_layout)

        self.label = QLabel(TEXT_1)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #f0f0f0;
                background-color: rgba(60, 60, 60, 0.8);
                padding: 15px;
                border-radius: 10px;
                border: 2px solid #808080;
            }
        """)
        self.label.setMinimumHeight(80)
        main_layout.addWidget(self.label)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        main_layout.addLayout(buttons_layout)

        self.text_is_changed = False
        
        button_style = """
            QPushButton {
                background-color: #606060;
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 150px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #707070;
            }
            QPushButton:pressed {
                background-color: #505050;
            }
        """

        self.button1 = QPushButton("Сменить текст")
        self.button1.clicked.connect(self.change_label_text)
        self.button1.setStyleSheet(button_style)
        buttons_layout.addWidget(self.button1)

        self.button2 = QPushButton("Загрузить изображение")
        self.button2.clicked.connect(self.load_transparent_image)
        self.button2.setStyleSheet(button_style)
        buttons_layout.addWidget(self.button2)

        self.background_pixmap = None
        self.central_widget.setAttribute(Qt.WA_TranslucentBackground)
        self.central_widget.setAutoFillBackground(False)
        self.central_widget.paintEvent = self.paint_background

    def paint_background(self, event):
        painter = QPainter(self.central_widget)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.background_pixmap:
            scaled_pixmap = self.background_pixmap.scaled(
                self.central_widget.size(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            painter.setOpacity(0.7)
            painter.drawPixmap(0, 0, scaled_pixmap)
        else:
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QColor(43, 43, 43))
            gradient.setColorAt(1, QColor(60, 60, 60))
            painter.fillRect(self.central_widget.rect(), gradient)
        
        painter.end()

    def change_label_text(self):
        if self.text_is_changed:
            self.label.setText(TEXT_1)
        else:
            self.label.setText(TEXT_2)

        self.text_is_changed = not self.text_is_changed

    def load_transparent_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Загрузите изображение",
            "",
            "PNG Files (*.png);;All Files (*)"
        )

        if not file_path:
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить изображение.")
            return

        self.background_pixmap = pixmap

        img_width = pixmap.width()
        img_height = pixmap.height()

        screen = self.screen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        if img_width > screen_width or img_height > screen_height:
            self.showMaximized()
        else:
            self.resize(img_width, img_height)

        self.central_widget.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
        
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())