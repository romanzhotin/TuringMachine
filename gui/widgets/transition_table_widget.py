from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTableWidget, QHeaderView, QLineEdit
from core.tape import Direction


class TransitionsTableWidget(QTableWidget):
    transition_changed = Signal(str, str, str, Direction, str)
    state_added = Signal(str)

    def __init__(self, alphabet_widget):
        super().__init__()
        self.alphabet_widget = alphabet_widget
        self.base_states = ["Q0"]
        self.dynamic_states = []
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        self._update_columns()
        self._update_rows()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)

    def _update_columns(self):
        all_states = self.base_states + self.dynamic_states
        self.setColumnCount(len(all_states))
        self.setHorizontalHeaderLabels(all_states)

    def _update_rows(self):
        alphabet = self.alphabet_widget.get_alphabet()
        self.setRowCount(len(alphabet))
        self.setVerticalHeaderLabels(alphabet)

        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if not self.cellWidget(row, col):
                    self._create_cell(row, col)

    def _create_cell(self, row, col):
        editor = QLineEdit()
        editor.setPlaceholderText("")
        self.setCellWidget(row, col, editor)
        return editor

    def _setup_connections(self):
        self.cellChanged.connect(self._process_cell_input)

    def _process_cell_input(self, row, col):
        editor = self.cellWidget(row, col)
        if not isinstance(editor, QLineEdit):
            return

        text = editor.text().strip()
        symbol_item = self.verticalHeaderItem(row)

        if not symbol_item:
            return

        symbol = symbol_item.text()
        current_state = self.horizontalHeaderItem(col).text()

        if self._validate_input(text):
            new_symbol, direction, target_state = self._parse_input(text)

            if target_state not in self.base_states + self.dynamic_states:
                self.dynamic_states.append(target_state)
                self._update_columns()
                self.state_added.emit(target_state)

            self.transition_changed.emit(
                current_state,
                symbol,
                new_symbol,
                direction,
                target_state
            )
            editor.setStyleSheet("")
        else:
            editor.setStyleSheet("background-color: #ffcccc;")

    @staticmethod
    def _validate_input(text: str) -> bool:
        if len(text) < 3:
            return False
        if text[1] not in {'>', '<', '!'}:
            return False
        if not text[2:].isdigit() and text[2:] != "a":
            return False
        return True

    @staticmethod
    def _parse_input(text: str):
        new_symbol = text[0].replace('_', ' ')
        direction = {
            '>': Direction.RIGHT,
            '<': Direction.LEFT,
            '!': Direction.STAY
        }[text[1]]
        state_suffix = text[2:]
        target_state = f"Q{state_suffix}" if state_suffix != "a" else "Qa"
        return new_symbol, direction, target_state

    def get_transitions(self):
        transitions = {}
        for row in range(self.rowCount()):
            symbol_item = self.verticalHeaderItem(row)
            if not symbol_item:
                continue
            symbol = symbol_item.text()

            for col in range(self.columnCount()):
                editor = self.cellWidget(row, col)
                if isinstance(editor, QLineEdit) and self._validate_input(editor.text()):
                    new_symbol, direction, target_state = self._parse_input(editor.text())
                    current_state = self.horizontalHeaderItem(col).text()
                    transitions[(current_state, symbol)] = (new_symbol, direction, target_state)
        return transitions

    def update_alphabet(self):
        self._update_rows()
