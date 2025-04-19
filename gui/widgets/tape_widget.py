from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget
)


class TapeCell(QWidget):
    def __init__(self, symbol=' ', position=0, current=False):
        super().__init__()
        self.current = current
        self.position = position
        self.editor = None

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.index_label = QLabel(str(position))
        self.index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.index_label.setStyleSheet('font: 12px Arial; color: #000000; font-weight: 500;')
        self.index_label.setFixedHeight(18)

        self.symbol_label = QLabel(str(symbol))
        self.symbol_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.symbol_label.setFixedSize(40, 40)

        self.layout.addWidget(self.index_label)
        self.layout.addWidget(self.symbol_label)
        self.setLayout(self.layout)
        self.update_style()
        self.setFixedHeight(59)

    def update_style(self):
        style = f"""
            font: 20px Arial;
            background: #f0f0f0;
            margin: 0px;
            padding: 0px;
            border: {'1px solid #000000' if self.current else 'none'};
            box-sizing: border-box;
        """
        self.symbol_label.setStyleSheet(style)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.editor is None:
            self.start_editing()
        super().mousePressEvent(event)

    def start_editing(self):
        self.editor = QLineEdit(self)
        current_text = self.symbol_label.text()
        self.editor.setText('' if current_text == ' ' else current_text)
        self.editor.setMaxLength(1)
        self.editor.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.editor.setGeometry(self.symbol_label.geometry())
        self.editor.setFont(self.symbol_label.font())

        self.editor.setStyleSheet(self.symbol_label.styleSheet())
        self.editor.setFocus()
        self.editor.selectAll()

        self.editor.editingFinished.connect(self.finish_edit)
        self.editor.show()

    def finish_edit(self):
        new_text = self.editor.text()
        if not new_text:
            new_text = ' '
        else:
            new_text = new_text[0]
        self.symbol_label.setText(new_text)
        self.editor.deleteLater()
        self.editor = None


class TapeWidget(QWidget):
    def __init__(self, visible_cell_count=13):
        super().__init__()
        self.visible_cell_count = visible_cell_count
        self.half_visible = visible_cell_count // 2
        self.current_position = 0
        self.cells = {}

        self.move_left_btn = QPushButton('←')
        self.move_right_btn = QPushButton('→')

        # Оригинальный стиль кнопок
        for btn in [self.move_left_btn, self.move_right_btn]:
            btn.setFixedSize(40, 58)
            btn.setStyleSheet("font: 20px Arial; padding-bottom: 5px;")

        self.move_left_btn.clicked.connect(self.move_left)
        self.move_right_btn.clicked.connect(self.move_right)

        self.inner_layout = QHBoxLayout()
        self.inner_layout.setContentsMargins(0, 0, 0, 0)
        self.inner_layout.setSpacing(1)
        self.inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.outer_layout = QHBoxLayout()
        self.outer_layout.setContentsMargins(10, 0, 10, 0)
        self.outer_layout.setSpacing(10)
        self.outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.outer_layout.addWidget(self.move_left_btn)
        self.outer_layout.addLayout(self.inner_layout)
        self.outer_layout.addWidget(self.move_right_btn)

        self.setLayout(self.outer_layout)
        self.setMinimumHeight(58)

        self.update_tape()

    def get_cell(self, position):
        if position not in self.cells:
            self.cells[position] = TapeCell(position=position)
        return self.cells[position]

    def update_tape(self):
        while self.inner_layout.count():
            item = self.inner_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        start = self.current_position - self.half_visible
        end = self.current_position + self.half_visible

        for pos in range(start, end + 1):
            cell = self.get_cell(pos)
            cell.current = (pos == self.current_position)
            cell.index_label.setText(str(pos))
            cell.update_style()
            self.inner_layout.addWidget(cell)

    def move_left(self):
        self.current_position -= 1
        self.update_tape()

    def move_right(self):
        self.current_position += 1
        self.update_tape()

    def write(self, symbol):
        if self.current_position in self.cells:
            self.cells[self.current_position].symbol_label.setText(str(symbol))

    def read(self):
        return self.cells[self.current_position].symbol_label.text() if self.current_position in self.cells else ' '
