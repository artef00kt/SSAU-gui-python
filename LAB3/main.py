import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QAction,
    QFileDialog,
    QMessageBox,
    QDialog,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
)


class QueryDialog(QDialog):
    """Модальное окно для ввода пользовательского SQL запроса"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выполнить SQL запрос")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("Введите SQL запрос:")
        label.setStyleSheet("font-size: 14px; color: #2c3e50; padding: 5px;")
        layout.addWidget(label)
        
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("SELECT * FROM table_name")
        self.query_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                background-color: #f8f9fa;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #ffffff;
            }
        """)
        layout.addWidget(self.query_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 13px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(buttons)
    
    def get_query(self):
        return self.query_input.text()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Viewer")
        self.setGeometry(100, 100, 1200, 700)
        
        # Переменные для работы с БД
        self.connection = None
        self.cursor = None
        self.db_path = None
        
        # Настройка стилей
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                min-width: 200px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
            QTabWidget::pane {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #bdc3c7;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #95a5a6;
            }
            QTableWidget {
                border: none;
                gridline-color: #bdc3c7;
                background-color: white;
                selection-background-color: #3498db;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Создаем меню
        self.create_menu()
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Первая строка кнопок
        top_button_layout = QHBoxLayout()
        top_button_layout.setSpacing(15)
        
        self.bt1 = QPushButton("SELECT Column")
        self.bt1.clicked.connect(self.select_column_query)
        self.bt1.setEnabled(False)
        top_button_layout.addWidget(self.bt1)
        
        top_button_layout.addStretch()
        
        self.combo_columns = QComboBox()
        self.combo_columns.addItem("Columns")
        self.combo_columns.currentIndexChanged.connect(self.column_selected)
        self.combo_columns.setEnabled(False)
        top_button_layout.addWidget(self.combo_columns)
        
        main_layout.addLayout(top_button_layout)
        
        # Вторая строка кнопок
        middle_button_layout = QHBoxLayout()
        middle_button_layout.setSpacing(15)
        
        self.bt2 = QPushButton("Query2")
        self.bt2.clicked.connect(self.query2)
        self.bt2.setEnabled(False)
        middle_button_layout.addWidget(self.bt2)
        
        middle_button_layout.addStretch()
        
        self.bt3 = QPushButton("Query3")
        self.bt3.clicked.connect(self.query3)
        self.bt3.setEnabled(False)
        middle_button_layout.addWidget(self.bt3)
        
        main_layout.addLayout(middle_button_layout)
        
        # TabWidget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Создаем 5 вкладок
        self.tables = []
        for i in range(1, 6):
            table = QTableWidget()
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionMode(QTableWidget.SingleSelection)
            self.tables.append(table)
            self.tab_widget.addTab(table, f"Tab{i}")
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # Меню File
        file_menu = menubar.addMenu("Menu")
        
        # Set connection
        connect_action = QAction("Set connection", self)
        connect_action.triggered.connect(self.set_connection)
        file_menu.addAction(connect_action)
        
        # Close connection
        close_action = QAction("Close connection", self)
        close_action.triggered.connect(self.close_connection)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        # Custom query
        custom_query_action = QAction("Custom Query...", self)
        custom_query_action.triggered.connect(self.show_custom_query_dialog)
        file_menu.addAction(custom_query_action)
    
    def set_connection(self):
        """Установить соединение с базой данных"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите базу данных SQLite",
            "",
            "SQLite Database (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Закрываем предыдущее соединение, если было
            if self.connection:
                self.connection.close()
            
            # Открываем новое соединение
            self.connection = sqlite3.connect(file_path)
            self.cursor = self.connection.cursor()
            self.db_path = file_path
            
            # Включаем кнопки
            self.bt1.setEnabled(True)
            self.bt2.setEnabled(True)
            self.bt3.setEnabled(True)
            self.combo_columns.setEnabled(True)
            
            # Выполняем первый запрос для Tab1
            self.execute_query("SELECT * FROM sqlite_master", 0)
            
            # Обновляем ComboBox с колонками
            self.update_columns_combo()
            
            QMessageBox.information(
                self,
                "Успех",
                f"Подключение к базе данных установлено!\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось подключиться к базе данных:\n{str(e)}"
            )
    
    def close_connection(self):
        """Закрыть соединение с базой данных"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
            self.db_path = None
            
            # Очищаем все таблицы
            for table in self.tables:
                table.clear()
                table.setRowCount(0)
                table.setColumnCount(0)
            
            # Отключаем кнопки
            self.bt1.setEnabled(False)
            self.bt2.setEnabled(False)
            self.bt3.setEnabled(False)
            self.combo_columns.setEnabled(False)
            
            # Очищаем ComboBox
            self.combo_columns.clear()
            self.combo_columns.addItem("Columns")
            
            QMessageBox.information(
                self,
                "Информация",
                "Соединение закрыто. Все данные очищены."
            )
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Соединение не установлено!"
            )
    
    def execute_query(self, query, tab_index):
        """Выполнить SQL запрос и вывести результат в указанную вкладку"""
        if not self.connection:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Сначала установите соединение с базой данных!"
            )
            return
        
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            # Получаем названия колонок
            if self.cursor.description:
                column_names = [description[0] for description in self.cursor.description]
            else:
                column_names = []
            
            # Заполняем таблицу
            table = self.tables[tab_index]
            table.clear()
            table.setRowCount(len(results))
            table.setColumnCount(len(column_names))
            table.setHorizontalHeaderLabels(column_names)
            
            for row_idx, row_data in enumerate(results):
                for col_idx, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data) if cell_data is not None else "")
                    table.setItem(row_idx, col_idx, item)
            
            # Автоматическая подгонка ширины колонок
            table.resizeColumnsToContents()
            
            # Переключаемся на эту вкладку
            self.tab_widget.setCurrentIndex(tab_index)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка SQL",
                f"Ошибка выполнения запроса:\n{str(e)}"
            )
    
    def select_column_query(self):
        """Кнопка bt1 - SELECT name FROM sqlite_master"""
        self.execute_query("SELECT name FROM sqlite_master", 1)
    
    def update_columns_combo(self):
        """Обновить список колонок в ComboBox"""
        try:
            # Получаем список таблиц
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            self.combo_columns.clear()
            self.combo_columns.addItem("Columns")
            
            # Для каждой таблицы получаем колонки
            for table_name in tables:
                table_name = table_name[0]
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = self.cursor.fetchall()
                
                for column in columns:
                    column_name = column[1]  # Имя колонки
                    self.combo_columns.addItem(f"{table_name}.{column_name}")
            
        except Exception as e:
            print(f"Ошибка при обновлении списка колонок: {e}")
    
    def column_selected(self, index):
        """Обработчик выбора колонки из ComboBox"""
        if index <= 0:  # Пропускаем "Columns"
            return
        
        selected = self.combo_columns.currentText()
        
        if '.' in selected:
            table_name, column_name = selected.split('.')
            query = f"SELECT {column_name} FROM {table_name}"
            self.execute_query(query, 2)
    
    def query2(self):
        """Кнопка bt2 - Query2"""
        # Получаем список всех таблиц и выводим первую из них
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            if tables:
                first_table = tables[0][0]
                query = f"SELECT * FROM {first_table}"
                self.execute_query(query, 3)
            else:
                QMessageBox.information(
                    self,
                    "Информация",
                    "В базе данных нет таблиц!"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка выполнения Query2:\n{str(e)}"
            )
    
    def query3(self):
        """Кнопка bt3 - Query3"""
        # Получаем список всех таблиц
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()
            
            if len(tables) > 1:
                second_table = tables[1][0]
                query = f"SELECT * FROM {second_table}"
                self.execute_query(query, 4)
            elif len(tables) == 1:
                # Если только одна таблица, показываем ее снова
                first_table = tables[0][0]
                query = f"SELECT * FROM {first_table} LIMIT 10"
                self.execute_query(query, 4)
            else:
                QMessageBox.information(
                    self,
                    "Информация",
                    "В базе данных нет таблиц!"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка выполнения Query3:\n{str(e)}"
            )
    
    def show_custom_query_dialog(self):
        """Показать модальное окно для ввода пользовательского запроса (БОНУС)"""
        if not self.connection:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Сначала установите соединение с базой данных!"
            )
            return
        
        dialog = QueryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            query = dialog.get_query()
            if query:
                # Определяем, в какую вкладку выводить (используем Tab2)
                self.execute_query(query, 1)
    
    def closeEvent(self, event):
        """Обработчик закрытия приложения"""
        if self.connection:
            self.connection.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

