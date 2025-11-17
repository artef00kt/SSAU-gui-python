import sqlite3
import os

def create_database():
    """Создание тестовой базы данных SQLite для демонстрации работы приложения"""
    
    db_path = 'database.db'
    
    # Удаляем старую базу, если существует
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Удалена старая база данных: {db_path}")
    
    # Создаем новое подключение
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Создаем таблицу студентов
        cursor.execute('''
            CREATE TABLE students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                course INTEGER,
                faculty TEXT
            )
        ''')
        print("✓ Таблица 'students' создана")
        
        # Создаем таблицу предметов
        cursor.execute('''
            CREATE TABLE subjects (
                id INTEGER PRIMARY KEY,
                subject_name TEXT NOT NULL,
                credits INTEGER,
                semester INTEGER
            )
        ''')
        print("✓ Таблица 'subjects' создана")
        
        # Создаем таблицу оценок
        cursor.execute('''
            CREATE TABLE grades (
                id INTEGER PRIMARY KEY,
                student_id INTEGER,
                subject_id INTEGER,
                grade INTEGER,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (subject_id) REFERENCES subjects(id)
            )
        ''')
        print("✓ Таблица 'grades' создана")
        
        # Заполняем таблицу студентов
        students_data = [
            (1, 'Иван Иванов', 20, 2, 'Информатика'),
            (2, 'Мария Петрова', 21, 3, 'Математика'),
            (3, 'Петр Сидоров', 19, 1, 'Информатика'),
            (4, 'Анна Смирнова', 22, 4, 'Физика'),
            (5, 'Дмитрий Козлов', 20, 2, 'Информатика'),
        ]
        cursor.executemany('INSERT INTO students VALUES (?, ?, ?, ?, ?)', students_data)
        print(f"✓ Добавлено {len(students_data)} студентов")
        
        # Заполняем таблицу предметов
        subjects_data = [
            (1, 'Математика', 5, 1),
            (2, 'Физика', 4, 1),
            (3, 'Программирование', 6, 2),
            (4, 'Базы данных', 5, 3),
            (5, 'Алгоритмы', 4, 2),
        ]
        cursor.executemany('INSERT INTO subjects VALUES (?, ?, ?, ?)', subjects_data)
        print(f"✓ Добавлено {len(subjects_data)} предметов")
        
        # Заполняем таблицу оценок
        grades_data = [
            (1, 1, 1, 5),
            (2, 1, 2, 4),
            (3, 2, 1, 5),
            (4, 2, 3, 5),
            (5, 3, 1, 3),
            (6, 3, 2, 4),
            (7, 4, 2, 5),
            (8, 5, 3, 4),
        ]
        cursor.executemany('INSERT INTO grades VALUES (?, ?, ?, ?)', grades_data)
        
        # Сохраняем изменения
        conn.commit()
        print(f"База данных '{db_path}' создана")
        print(f"   - students: {len(students_data)} записей")
        print(f"   - subjects: {len(subjects_data)} записей")
        print(f"   - grades: {len(grades_data)} записей")
        
    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        conn.rollback()
    
    finally:
        conn.close()


if __name__ == "__main__":
    create_database()

