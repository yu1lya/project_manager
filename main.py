import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QComboBox,
    QDialog,
)

from PyQt6.QtCore import Qt


class EditProjectDialog(QDialog):
    def __init__(self, project_data, parent=None):
        super(EditProjectDialog, self).__init__(parent)
        self.setWindowTitle("Редактирование проекта")
        self.setGeometry(150, 150, 400, 300)

        self.layout = QVBoxLayout(self)

        # Поле для названия проекта
        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Название проекта")
        self.title_input.setText(project_data[1])  # Загружаем название
        self.layout.addWidget(self.title_input)

        # Выпадающий список для статуса
        self.status_input = QComboBox(self)
        self.status_input.addItems(["В процессе", "Завершен", "Отложен"])
        self.status_input.setCurrentText(project_data[2])  # Загружаем статус
        self.layout.addWidget(self.status_input)

        # Метка для отображения файла
        self.file_label = QLabel(f"Файл: {project_data[3]}", self)
        self.layout.addWidget(self.file_label)

        # Кнопка для выбора нового файла
        self.change_file_button = QPushButton("Выбрать другой файл", self)
        self.change_file_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.change_file_button)

        # Кнопка для сохранения изменений
        self.save_button = QPushButton("Сохранить изменения", self)
        self.save_button.clicked.connect(lambda: self.save_changes(project_data[0]))  # ID проекта
        self.layout.addWidget(self.save_button)

        self.selected_file_path = project_data[3]  # Сохранили путь к текущему файлу

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать файл", "", "All Files (*);;Text Files (*.txt)")
        if file_path:
            self.selected_file_path = file_path  # Обновляем путь к файлу
            self.file_label.setText(f"Файл: {self.selected_file_path}")  # Обновляем метку для файла

    def save_changes(self, project_id):
        title = self.title_input.text()
        status = self.status_input.currentText()

        try:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE projects SET title=?, status=?, file_path=? WHERE id=?',
                               (title, status, self.selected_file_path, project_id))
                conn.commit()
            QMessageBox.information(self, "Успех", "Проект успешно отредактирован!")
            self.accept()  # Закрывает диалог
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {e}")


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        self.setWindowTitle("ProjectX")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(20)
        self.layout.setContentsMargins(20, 20, 20, 20)

        self.project_title_input = QLineEdit(self)
        self.project_title_input.setPlaceholderText("Название проекта")
        self.layout.addWidget(self.project_title_input)

        self.status_input = QComboBox(self)
        self.status_input.addItems(["В процессе", "Завершен", "Отложен"])
        self.layout.addWidget(self.status_input)

        self.upload_file_button = QPushButton("Загрузить файл", self)
        self.upload_file_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_file_button)

        self.loaded_file_label = QLabel("Загруженный файл:", self)
        self.layout.addWidget(self.loaded_file_label)

        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        self.add_project_button = QPushButton("Добавить проект", self)
        self.add_project_button.clicked.connect(self.add_project)
        self.buttons_layout.addWidget(self.add_project_button)

        self.edit_project_button = QPushButton("Редактировать проект", self)
        self.edit_project_button.clicked.connect(self.edit_project)
        self.buttons_layout.addWidget(self.edit_project_button)

        self.delete_project_button = QPushButton("Удалить проект", self)
        self.delete_project_button.clicked.connect(self.delete_project)
        self.buttons_layout.addWidget(self.delete_project_button)

        self.projects_table = QTableWidget(self)
        self.projects_table.setColumnCount(4)  # 4 колонки: Название, Статус, Файл, ID
        self.projects_table.setHorizontalHeaderLabels(["Название", "Статус", "Файл", "ID"])
        self.layout.addWidget(self.projects_table)

        self.current_file_path = None
        self.create_table()
        self.load_projects()

    def create_table(self):
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    file_path TEXT
                )
            """)
            conn.commit()

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать файл", "", "All Files (*);;Text Files (*.txt)")
        if file_path:
            self.loaded_file_label.setText(f"Загруженный файл: {file_path}")
            self.current_file_path = file_path

    def add_project(self):
        title = self.project_title_input.text()
        status = self.status_input.currentText()
        if self.current_file_path:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO projects (title, status, file_path) VALUES (?, ?, ?)',
                               (title, status, self.current_file_path))
                conn.commit()
            self.load_projects()
            self.clear_inputs()
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, загрузите файл перед добавлением проекта.")

    def load_projects(self):
        self.projects_table.setRowCount(0)  # Очистить таблицу
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, title, status, file_path FROM projects')
            projects = cursor.fetchall()
            for project in projects:
                row_position = self.projects_table.rowCount()
                self.projects_table.insertRow(row_position)
                self.projects_table.setItem(row_position, 0, QTableWidgetItem(project[1]))  # Название
                self.projects_table.setItem(row_position, 1, QTableWidgetItem(project[2]))  # Статус
                self.projects_table.setItem(row_position, 2, QTableWidgetItem(project[3]))  # Файл
                self.projects_table.setItem(row_position, 3, QTableWidgetItem(str(project[0])))  # ID

    def clear_inputs(self):
        self.project_title_input.clear()
        self.status_input.setCurrentIndex(0)  # Сбросить выбор
        self.loaded_file_label.setText("Загруженный файл:")  # Сбросить метку файла
        self.current_file_path = None

    def edit_project(self):
        selected_row = self.projects_table.currentRow()  # Проверка, выбран ли проект
        if selected_row >= 0:
            project_data = (
                self.projects_table.item(selected_row, 3).text(),  # ID
                self.projects_table.item(selected_row, 0).text(),  # Название
                self.projects_table.item(selected_row, 1).text(),  # Статус
                self.projects_table.item(selected_row, 2).text(),  # Файл
            )
            dialog = EditProjectDialog(project_data, self)
            dialog.exec()  # Открыть диалог редактирования модально
            self.load_projects()  # Обновление таблицы после редактирования
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите проект для редактирования.")

    def delete_project(self):
        selected_row = self.projects_table.currentRow()  # Проверка, выбран ли проект
        if selected_row >= 0:
            project_id = self.projects_table.item(selected_row, 3).text()  # Получаем ID проекта
            button_yes = QMessageBox.question(self, "Удаление", "Вы уверены, что хотите удалить этот проект?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if button_yes == QMessageBox.StandardButton.Yes:
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM projects WHERE id=?', (project_id,))
                    conn.commit()
                self.load_projects()  # Обновляем таблицу проектов
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите проект для удаления.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec())