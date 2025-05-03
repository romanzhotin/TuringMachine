import platform

from pathlib import Path
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget
)

from core.tape import TuringTape
from gui.dialogs.about_dialog import AboutDialog
from gui.menu.menu import MainAppMenuBar
from gui.widgets.alphabet_widget import AlphabetWidget
from gui.widgets.notes_widget import NotesWidget
from gui.widgets.tape_widget import TapeWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Машина Тьюринга")
        self.setFocus()
        self._setup_ui()
        self._connect_menu_signals()
        self._apply_styles()

    def _setup_ui(self):
        self.menu_bar = MainAppMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.statusBar().showMessage('')

        tape = TuringTape()
        self.alphabet_widget = AlphabetWidget(width=1050)
        self.tape_widget = TapeWidget(
            tape=tape,
            alphabet_widget=self.alphabet_widget,
            window_size=10,
            cell_size=50
        )
        self.notes_widget = NotesWidget()

        central = QWidget()

        layout_1 = QVBoxLayout()
        layout_1.addWidget(self.tape_widget)
        layout_1.addWidget(self.alphabet_widget)
        layout_1.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        layout_2 = QHBoxLayout()
        layout_2.addLayout(layout_1)
        layout_2.addWidget(self.notes_widget)

        layout_3 = QVBoxLayout()
        layout_3.addLayout(layout_2)

        central.setLayout(layout_3)
        self.setCentralWidget(central)

        self.tape_widget.error_message.connect(self.statusBar().showMessage)

    def _connect_menu_signals(self):
        # file_menu
        self.menu_bar.new_requested.connect(self.new_file)
        self.menu_bar.open_requested.connect(self.open_file)
        self.menu_bar.save_requested.connect(self.save_file)
        self.menu_bar.save_as_requested.connect(self.save_as_file)
        self.menu_bar.exit_requested.connect(self.exit)

        # run_menu
        self.menu_bar.run_requested.connect(self.run_program)

        # options_menu
        self.menu_bar.options_dialog_requested.connect(self.show_options_dialog)

        # help_menu
        self.menu_bar.help_requested.connect(self.help_show)
        self.menu_bar.about_dialog_requested.connect(self.show_about_dialog)

    def _apply_styles(self):
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        os_name = platform.system().lower()

        if os_name == 'linux':
            style_path = project_root / 'styles' / 'light' / 'linux.qss'
        elif os_name == 'windows':
            style_path = project_root / 'styles' / 'light' / 'windows.qss'
        else:
            return

        with open(style_path, 'r', encoding='utf-8') as file:
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
    def show_options_dialog(self):
        print('Настройки')

    @Slot()
    def help_show(self):
        print('Справка о программе')

    @Slot()
    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.show()
