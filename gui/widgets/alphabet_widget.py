from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit


class AlphabetWidget(QWidget):
    text_processed = Signal(str)

    def __init__(self, width: int = 1050):
        super().__init__()
        self.width = width
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel('Алфавит')
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Пример: 01abc')

        self.setFixedSize(self.width, 80)

        layout.addWidget(self.label)
        layout.addWidget(self.input_field)
        self.setLayout(layout)

    def _connect_signals(self):
        self.input_field.editingFinished.connect(self._process_input)

    def _process_input(self):
        text = sorted(list(set(self.input_field.text())))
        res = ''.join(text)
        self.input_field.setText(res)
        self.text_processed.emit(res)

    def get_alphabet(self):
        return sorted(list(set(self.input_field.text())))
