import platform

from pathlib import Path
from PySide6.QtCore import Slot, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QMessageBox
)

from core.machine import TuringMachine
from core.tape import TuringTape

from gui.dialogs.about_dialog import AboutDialog
from gui.dialogs.error_dialog import ErrorDialog

from gui.menu.menu import MainAppMenuBar

from gui.widgets.alphabet_widget import AlphabetWidget
from gui.widgets.notes_widget import NotesWidget
from gui.widgets.tape_widget import TapeWidget
from gui.widgets.transition_table_widget import TransitionsTableWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Машина Тьюринга")
        self.setFocus()
        self._machine = None
        self._timer = QTimer(self)
        self._speed_delay = 400

        self._setup_ui()
        self._connect_menu_signals()

        self._timer.timeout.connect(self._animate_step)

    def _setup_ui(self):
        self.menu_bar = MainAppMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.statusBar().showMessage("")

        tape = TuringTape()
        self.alphabet_widget = AlphabetWidget(width=1050)
        self.tape_widget = TapeWidget(
            tape=tape,
            alphabet_widget=self.alphabet_widget,
            window_size=10,
            cell_size=50
        )
        self.transitions_table = TransitionsTableWidget(self.alphabet_widget)
        self.notes_widget = NotesWidget()

        central = QWidget()

        self.tape_input = QLineEdit()
        self.tape_input.setPlaceholderText("Введите начальную строку ленты (например: 0101)")
        self.tape_input.returnPressed.connect(self._load_tape)
        btn_load = QPushButton("Загрузить на ленту")
        btn_load.clicked.connect(self._load_tape)

        tape_control_layout = QHBoxLayout()
        tape_control_layout.addWidget(self.tape_input)
        tape_control_layout.addWidget(btn_load)

        layout_1 = QVBoxLayout()
        layout_1.addLayout(tape_control_layout)
        layout_1.addWidget(self.tape_widget)
        layout_1.addWidget(self.alphabet_widget)
        layout_1.addWidget(self.transitions_table)
        layout_1.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        layout_2 = QHBoxLayout()
        layout_2.addLayout(layout_1)
        layout_2.addWidget(self.notes_widget)

        central.setLayout(layout_2)
        self.setCentralWidget(central)

        self.tape_widget.error_message.connect(self.statusBar().showMessage)
        self.alphabet_widget.text_processed.connect(self.transitions_table.update_alphabet)
        self.menu_bar.speed_changed.connect(self._update_speed)

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

    @Slot()
    def new_file(self):
        if self._timer.isActive():
            self._timer.stop()
        self.tape_widget.tape.reset("")
        self.tape_widget.update_view()
        self.alphabet_widget.input_field.clear()
        self.transitions_table.dynamic_states = []
        self.transitions_table.base_states = ["Q0"]
        self.transitions_table._update_columns()
        self.transitions_table.update_alphabet()
        self.notes_widget.task_edit.clear()
        self.notes_widget.comments_edit.clear()
        self.statusBar().showMessage("Новый файл создан")
        self._machine = None

    @Slot()
    def open_file(self):
        print("Открытие файла")

    @Slot()
    def save_file(self):
        print("Сохранение файла")

    @Slot()
    def save_as_file(self):
        print("Сохранение как")

    @Slot()
    def exit(self):
        QApplication.quit()

    @Slot()
    def run_program(self):
        try:
            if self._timer.isActive():
                self._timer.stop()

            transitions = self.transitions_table.get_transitions()
            if not transitions:
                ErrorDialog("Нет переходов в таблице!", self).show()
                return

            alphabet = set(self.alphabet_widget.get_alphabet())
            for (state, symbol), (new_symbol, direction, target_state) in transitions.items():
                if symbol not in alphabet or new_symbol not in alphabet:
                    ErrorDialog(f"Символ '{symbol}' или '{new_symbol}' не входит в алфавит!", self).show()
                    return

            self._machine = TuringMachine(
                initial_state="Q0",
                final_states={"Qa"},
                transition_table=transitions,
                tape=self.tape_widget.tape,
                alphabet=alphabet,
                max_steps=1000
            )

            self.tape_widget.update_view()
            self._timer.start(self._speed_delay)

        except Exception as e:
            ErrorDialog(f"Критическая ошибка: {str(e)}", self).show()

    @Slot()
    def _animate_step(self):
        if not self._machine or self._machine.is_halted:
            self._timer.stop()
            if self._machine and self._machine.error_occurred:
                ErrorDialog(self._machine.error_message, self).show()
            elif self._machine and not self._machine.error_occurred:
                self.statusBar().showMessage("Выполнение завершено")
            return

        current_state = self._machine.get_current_state()
        current_symbol = self.tape_widget.tape.read()
        self.transitions_table.highlight(current_state, current_symbol)

        ok = self._machine.step()
        self.tape_widget.update_view()
        if not ok or self._machine.is_halted:
            self._timer.stop()
            if self._machine.error_occurred:
                ErrorDialog(self._machine.error_message, self).show()
            else:
                self.statusBar().showMessage("Выполнение завершено")

    @Slot(int)
    def _update_speed(self, delay):
        self._speed_delay = delay
        if self._timer.isActive():
            self._timer.setInterval(self._speed_delay)

    @Slot()
    def _load_tape(self):
        s = self.tape_input.text()
        if not s:
            self.statusBar().showMessage("Строка ленты пуста")
            return

        current_alphabet = set(self.alphabet_widget.get_alphabet())
        tape_symbols = set(s)
        missing = tape_symbols - current_alphabet
        if missing:
            msg = QMessageBox(self)
            msg.setWindowTitle("Недопустимые символы")
            msg.setText(f"Символы {', '.join(missing)} отсутствуют в алфавите.\nДобавить их?")
            btn_yes = msg.addButton("Да", QMessageBox.YesRole)
            btn_no = msg.addButton("Нет", QMessageBox.NoRole)
            msg.exec()

            if msg.clickedButton() == btn_yes:
                existing_text = self.alphabet_widget.input_field.text().replace(" ", "")
                new_text = existing_text + "".join(sorted(missing))
                self.alphabet_widget.input_field.setText(new_text)
                self.alphabet_widget.text_processed.emit(new_text)
            else:
                self.statusBar().showMessage("Загрузка ленты отменена")
                return

        self.tape_widget.tape.reset(s)
        self.tape_widget.update_view()
        self.statusBar().showMessage(f"Лента загружена: '{s}'")

    @Slot()
    def show_options_dialog(self):
        print("Настройки")

    @Slot()
    def help_show(self):
        print("Справка о программе")

    @Slot()
    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.show()
