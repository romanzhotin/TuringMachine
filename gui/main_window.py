import json

from PySide6.QtCore import Slot, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFileDialog
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
        self._machine = None
        self._timer = QTimer(self)
        self._speed_delay = 400
        self._current_file = None

        self._setup_ui()
        self._connect_menu_signals()

        self._timer.timeout.connect(self._animate_step)
        self._update_window_title()

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

    def _update_window_title(self):
        if self._current_file:
            name = self._current_file.split("/")[-1]
        else:
            name = "<Новый файл>"
        self.setWindowTitle(f"Машина Тьюринга — {name}")

    @Slot()
    def new_file(self):
        if self._timer.isActive():
            self._timer.stop()

        if self._current_file is not None:
            msg = QMessageBox(self)
            msg.setWindowTitle("Новый файл")
            msg.setText("Сохранить текущий файл перед созданием нового?")

            btn_yes = msg.addButton("Да", QMessageBox.ButtonRole.YesRole)
            msg.addButton("Нет", QMessageBox.ButtonRole.NoRole)
            btn_cancel = msg.addButton("Отмена", QMessageBox.ButtonRole.RejectRole)

            msg.setDefaultButton(btn_yes)
            msg.exec()

            clicked = msg.clickedButton()
            if clicked == btn_yes:
                saved = self.save_file()
                if saved is False:
                    return
            elif clicked == btn_cancel:
                return

        self._current_file = None
        self.alphabet_widget.input_field.clear()
        self.alphabet_widget.text_processed.emit("")

        self.tape_input.clear()
        self.tape_widget.tape.reset("")
        self.tape_widget.update_view()

        self.transitions_table.dynamic_states = []
        self.transitions_table.base_states = ["Q0"]
        self.transitions_table.update_alphabet()

        self.notes_widget.task_edit.clear()
        self.notes_widget.comments_edit.clear()

        self.statusBar().showMessage("Новый файл создан")
        self._machine = None
        self._update_window_title()

    @Slot()
    def open_file(self):
        if self._timer.isActive():
            self._timer.stop()

        if self._current_file is not None:
            msg = QMessageBox(self)
            msg.setWindowTitle("Открыть файл")
            msg.setText("Сохранить текущий файл перед открытием нового?")

            btn_yes = msg.addButton("Да", QMessageBox.ButtonRole.YesRole)
            msg.addButton("Нет", QMessageBox.ButtonRole.NoRole)
            btn_cancel = msg.addButton("Отмена", QMessageBox.ButtonRole.RejectRole)

            msg.setDefaultButton(btn_yes)
            msg.exec()

            clicked = msg.clickedButton()
            if clicked == btn_yes:
                saved = self.save_file()
                if saved is False:
                    return
            elif clicked == btn_cancel:
                return

        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Открыть файл",
            "",
            "JSON Files (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            ErrorDialog(f"Ошибка чтения файла: {str(e)}", self).show()
            return

        if not isinstance(data, dict):
            ErrorDialog("Некорректный формат: не объект JSON", self).show()
            return

        required_keys = {"alphabet", "tape", "transitions", "notes"}
        if not required_keys.issubset(data.keys()):
            ErrorDialog("В файле отсутствуют обязательные ключи", self).show()
            return

        alphabet = data["alphabet"]
        if not isinstance(alphabet, list) or not all(isinstance(ch, str) for ch in alphabet):
            ErrorDialog("Алфавит должен быть списком строк", self).show()
            return
        self.alphabet_widget.input_field.setText("".join(alphabet).replace(" ", ""))
        self.alphabet_widget.text_processed.emit("".join(alphabet))

        tape_str = data["tape"]
        if not isinstance(tape_str, str):
            ErrorDialog("Лента должна быть строкой", self).show()
            return
        self.tape_input.setText(tape_str)
        self.tape_widget.tape.reset(tape_str)
        self.tape_widget.update_view()

        transitions = data["transitions"]
        if not isinstance(transitions, dict):
            ErrorDialog("Неправильный формат transitions", self).show()
            return

        self.transitions_table.dynamic_states = []
        self.transitions_table.base_states = ["Q0"]
        self.transitions_table.update_alphabet()

        for state, rules in transitions.items():
            if not isinstance(rules, dict):
                continue
            if state not in (self.transitions_table.base_states + self.transitions_table.dynamic_states):
                self.transitions_table.dynamic_states.append(state)
                self.transitions_table.update_alphabet()

            for symbol, rule in rules.items():
                if (
                        not isinstance(symbol, str)
                        or not isinstance(rule, dict)
                        or "new_symbol" not in rule
                        or "direction" not in rule
                        or "next_state" not in rule
                ):
                    continue

                new_symbol = rule["new_symbol"]
                direction = rule["direction"]
                next_state = rule["next_state"]

                dir_char = "!"
                if direction == "LEFT":
                    dir_char = "<"
                elif direction == "RIGHT":
                    dir_char = ">"

                suffix = next_state[1:] if next_state.startswith("Q") else next_state
                if next_state == "Qa":
                    suffix = "a"

                cell_text = f"{new_symbol}{dir_char}{suffix}"

                all_states = self.transitions_table.base_states + self.transitions_table.dynamic_states
                try:
                    col = all_states.index(state)
                except ValueError:
                    continue

                row = None
                for i in range(self.transitions_table.table.rowCount()):
                    if self.transitions_table.table.verticalHeaderItem(i).text() == symbol:
                        row = i
                        break
                if row is None:
                    continue

                editor = self.transitions_table.table.cellWidget(row, col)
                if editor:
                    editor.setText(cell_text)

        notes = data["notes"]
        if isinstance(notes, dict):
            task = notes.get("task", "")
            comments = notes.get("comments", "")
            if isinstance(task, str):
                self.notes_widget.task_edit.setPlainText(task)
            if isinstance(comments, str):
                self.notes_widget.comments_edit.setPlainText(comments)

        self._current_file = file_path
        self.statusBar().showMessage(f"Файл загружен: {file_path}")
        self._update_window_title()

    @Slot()
    def save_file(self):
        if not self._current_file:
            return self.save_as_file()

        data = self._gather_project_data()
        try:
            with open(self._current_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)  # type: ignore
            self.statusBar().showMessage(f"Сохранено: {self._current_file}")
            self._update_window_title()
        except Exception as e:
            ErrorDialog(f"Ошибка сохранения: {str(e)}", self).show()
            return False
        return True

    @Slot()
    def save_as_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Сохранить как",
            "",
            "JSON Files (*.json)"
        )
        if not file_path:
            return False
        if not file_path.lower().endswith(".json"):
            file_path += ".json"
        self._current_file = file_path
        return self.save_file()

    def _gather_project_data(self):
        alphabet = self.alphabet_widget.get_alphabet()
        tape_str = str(self.tape_widget.tape)

        transitions_raw = self.transitions_table.get_transitions()
        transitions = {}
        for (state, symbol), (new_symbol, direction_enum, next_state) in transitions_raw.items():
            direction = (
                "LEFT" if direction_enum.name == "LEFT"
                else "RIGHT" if direction_enum.name == "RIGHT"
                else "STAY"
            )
            transitions.setdefault(state, {})[symbol] = {
                "new_symbol": new_symbol,
                "direction": direction,
                "next_state": next_state
            }

        notes = {
            "task": self.notes_widget.task_edit.toPlainText(),
            "comments": self.notes_widget.comments_edit.toPlainText()
        }

        return {
            "alphabet": alphabet,
            "tape": tape_str,
            "transitions": transitions,
            "notes": notes
        }

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
            btn_yes = msg.addButton("Да", QMessageBox.ButtonRole.YesRole)
            msg.addButton("Нет", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(btn_yes)
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
