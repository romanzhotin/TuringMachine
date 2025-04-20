import platform


from pathlib import Path
from PySide6.QtCore import QFile, Slot
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget
)
from gui.dialogs.about_dialog import AboutDialog
from gui.menu.menu import MainAppMenuBar
from gui.widgets.tape_widget import TapeWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Turing Machine')
        self._setup_ui()
        self._connect_menu_signals()
        self._apply_styles()

    def _setup_ui(self):
        self.menu_bar = MainAppMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self.statusBar().showMessage('')

        self.tape_widget = TapeWidget(visible_cell_count=27)
        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tape_widget)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _connect_menu_signals(self):
        # file_menu
        self.menu_bar.new_requested.connect(self.new_file)
        self.menu_bar.open_requested.connect(self.open_file)
        self.menu_bar.save_requested.connect(self.save_file)
        self.menu_bar.save_as_requested.connect(self.save_as_file)
        self.menu_bar.exit_requested.connect(self.exit)

        # run_menu
        self.menu_bar.run_requested.connect(self.run_program)

        # help_menu
        self.menu_bar.help_requested.connect(self.help_show)
        self.menu_bar.about_dialog_requested.connect(self.show_about_dialog)

    def _apply_styles(self):
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        os_name = platform.system().lower()
        if os_name == 'linux':
            style_path = project_root / 'styles' / 'light_linux.qss'
            with open(style_path, 'r') as file:
                style = file.read()
        elif os_name == 'windows':
            style_path = project_root / 'styles' / 'light_windows.qss'
            with open(style_path, 'r') as file:
                style = file.read()
        self.setStyleSheet(style)

    @Slot()
    def new_file(self):
        print('Создан новый файл')

    @Slot()
    def open_file(self):
        print('Открытие файла')

    @Slot()
    def save_file(self):
        print('Сохранение файла')

    @Slot()
    def save_as_file(self):
        print('Сохранение как')

    @Slot()
    def exit(self):
        QApplication.quit()

    @Slot()
    def run_program(self):
        print('Программа запущена')

    @Slot()
    def help_show(self):
        print('Справка о программе')

    @Slot()
    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()
