from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QTableWidget, QHeaderView, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout
from core.tape import Direction


class CellEditor(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("")


class TransitionsTableWidget(QWidget):
    transition_changed = Signal(str, str, str, Direction, str)
    state_added = Signal(str)
    state_removed = Signal(str)

    def __init__(self, alphabet_widget):
        super().__init__()
        self.alphabet_widget = alphabet_widget
        self.base_states = ["Q0"]
        self.dynamic_states = []
        self._highlighted = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)

        self.add_btn = QPushButton("Add State")
        self.remove_btn = QPushButton("Remove State")

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.table)

        self._update_columns()
        self.update_alphabet()

    def _connect_signals(self):
        self.table.cellChanged.connect(self._process_cell_input)
        self.add_btn.clicked.connect(self.add_state)
        self.remove_btn.clicked.connect(self.remove_state)
        self.alphabet_widget.text_processed.connect(self.update_alphabet)

    def _update_columns(self):
        all_states = self.base_states + self.dynamic_states
        self.table.setColumnCount(len(all_states))
        self.table.setHorizontalHeaderLabels(all_states)

    def update_alphabet(self):
        old_alphabet = [self.table.verticalHeaderItem(r).text() for r in range(self.table.rowCount())]
        old_states = self.base_states + self.dynamic_states
        old_data = {}
        for r, symbol in enumerate(old_alphabet):
            for c, state in enumerate(old_states):
                editor = self.table.cellWidget(r, c)
                if isinstance(editor, QLineEdit):
                    old_data[(state, symbol)] = editor.text()

        new_alphabet = self.alphabet_widget.get_alphabet()
        self._update_columns()
        self.table.clearContents()
        self.table.setRowCount(len(new_alphabet))
        self.table.setVerticalHeaderLabels(new_alphabet)

        for r, symbol in enumerate(new_alphabet):
            for c, state in enumerate(self.base_states + self.dynamic_states):
                editor = CellEditor()
                txt = old_data.get((state, symbol), '')
                editor.setText(txt)
                self.table.setCellWidget(r, c, editor)

    def add_state(self):
        idx = len(self.dynamic_states) + 1
        new_state = f"Q{idx}"
        self.dynamic_states.append(new_state)
        self._update_columns()
        self.update_alphabet()
        self.state_added.emit(new_state)

    def remove_state(self):
        if not self.dynamic_states:
            return
        last = self.dynamic_states.pop()
        self._update_columns()
        self.update_alphabet()
        self.state_removed.emit(last)

    def _process_cell_input(self, row, col):
        editor = self.table.cellWidget(row, col)
        if not isinstance(editor, QLineEdit):
            return
        text = editor.text().strip()
        symbol = self.table.verticalHeaderItem(row).text()
        current_state = self.table.horizontalHeaderItem(col).text()
        alphabet = self.alphabet_widget.get_alphabet()

        if self._validate_input(text, alphabet):
            new_symbol, direction, target_state = self._parse_input(text)
            if target_state not in self.base_states + self.dynamic_states:
                self.dynamic_states.append(target_state)
                self._update_columns()
                self.update_alphabet()
                self.state_added.emit(target_state)
            self.transition_changed.emit(current_state, symbol, new_symbol, direction, target_state)
            editor.setStyleSheet("")
        else:
            editor.setStyleSheet("background-color: #ffdddd;")

    @staticmethod
    def _validate_input(text: str, alphabet: list) -> bool:
        if len(text) < 3:
            return False
        if text[1] not in {'>', '<', '!'}:
            return False
        if text[0] not in alphabet:
            return False
        if not text[2:].isdigit() and text[2:] != "a":
            return False
        return True

    @staticmethod
    def _parse_input(text: str):
        new_symbol = text[0]
        direction = {'>': Direction.RIGHT, '<': Direction.LEFT, '!': Direction.STAY}[text[1]]
        suffix = text[2:]
        target_state = f"Q{suffix}" if suffix != 'a' else 'Qa'
        return new_symbol, direction, target_state

    def get_transitions(self):
        transitions = {}
        for r in range(self.table.rowCount()):
            symbol = self.table.verticalHeaderItem(r).text()
            for c, state in enumerate(self.base_states + self.dynamic_states):
                editor = self.table.cellWidget(r, c)
                if isinstance(editor, QLineEdit) and \
                   self._validate_input(editor.text().strip(), self.alphabet_widget.get_alphabet()):
                    new_symbol, direction, target_state = self._parse_input(editor.text().strip())
                    current_state = state
                    transitions[(current_state, symbol)] = (new_symbol, direction, target_state)
        return transitions

    def highlight(self, state: str, symbol: str):
        if self._highlighted:
            prev_r, prev_c = self._highlighted
            prev_widget = self.table.cellWidget(prev_r, prev_c)
            if prev_widget:
                prev_widget.setStyleSheet("")

        all_states = self.base_states + self.dynamic_states
        try:
            c = all_states.index(state)
        except ValueError:
            return

        try:
            r = [
                self.table.verticalHeaderItem(i).text()
                for i in range(self.table.rowCount())
            ].index(symbol)
        except ValueError:
            return

        widget = self.table.cellWidget(r, c)
        if widget:
            widget.setStyleSheet("background-color: #ff9999;")
            self._highlighted = (r, c)
