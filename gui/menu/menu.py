from PySide6.QtCore import Signal
from PySide6.QtGui import (
    QAction,
    QKeySequence
)
from PySide6.QtWidgets import (
    QMenu,
    QMenuBar
)


class MainAppMenuBar(QMenuBar):
    # file_menu
    new_requested = Signal()
    open_requested = Signal()
    save_requested = Signal()
    save_as_requested = Signal()
    exit_requested = Signal()

    # run_menu
    run_requested = Signal()

    # help_menu
    help_requested = Signal()
    about_dialog_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self._create_file_menu()
        self._create_run_menu()
        self._create_help_menu()

    def _create_file_menu(self):
        file_menu = QMenu('Файл', self)

        actions = [
            ('Новый\tCtrl+N', QKeySequence('Ctrl+N'), self.new_requested),
            ('Открыть\tCtrl+O', QKeySequence('Ctrl+O'), self.open_requested),
            ('Сохранить\tCtrl+S', QKeySequence('Ctrl+S'), self.save_requested),
            ('Сохранить как\tCtrl+Shift+S', QKeySequence('Ctrl+Shift+S'), self.save_as_requested),
            ('Выход\tCtrl+Q', QKeySequence('Ctrl+Q'), self.exit_requested)
        ]

        for text, shortcut, handler in actions:
            action = QAction(text, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(handler)
            file_menu.addAction(action)

        self.addMenu(file_menu)

    def _create_run_menu(self):
        run_menu = QMenu('Запуск', self)

        actions = [
            ('Запустить\tF5', QKeySequence('F5'), self.run_requested)
        ]

        for text, shortcut, handler in actions:
            action = QAction(text, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(handler)
            run_menu.addAction(action)

        self.addMenu(run_menu)

    def _create_help_menu(self):
        help_menu = QMenu('Помощь', self)

        actions = [
            ('Справка\tF1', QKeySequence('F1'), self.help_requested),
            ('О программе\t', QKeySequence(), self.about_dialog_requested)
        ]

        for text, shortcut, handler in actions:
            action = QAction(text, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(handler)
            help_menu.addAction(action)

        self.addMenu(help_menu)
