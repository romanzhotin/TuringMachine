from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QSizePolicy
)
from core.tape import TuringTape, Direction


class Cell(QLineEdit):
    def __init__(self, idx, tape_widget):
        super().__init__(tape_widget.tape.blank)
        self.idx = idx
        self.tape_widget = tape_widget
        self.setMaxLength(1)
        self.setFixedSize(tape_widget.cell_size, tape_widget.cell_size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def keyPressEvent(self, event):
        key = event.text()
        if key == ' ' and not event.modifiers():  # Если нажали пробел, вставляем '_'
            key = '_'
        if key and not event.modifiers():
            pos = self.tape_widget.tape.head - self.tape_widget.window + self.idx
            self.tape_widget.tape.tape[pos] = key
            self.setText(key)
        else:
            super().keyPressEvent(event)


class TapeWidget(QWidget):
    def __init__(self, tape: TuringTape, window_size: int = 10, cell_size: int = 30):
        super().__init__()
        self.tape = tape
        self.window = window_size
        self.cell_size = cell_size
        self.index_labels = []
        self.cells = []
        self._setup_ui()
        self.setFixedSize(QSize(self.calculate_fixed_size()[0], self.calculate_fixed_size()[1]))

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        index_layout = QHBoxLayout()
        index_layout.setSpacing(0)
        for idx in range(2 * self.window + 1):
            lbl = QLabel("")
            lbl.setFixedSize(self.cell_size, self.cell_size // 2)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            index_layout.addWidget(lbl)
            self.index_labels.append(lbl)
        main_layout.addLayout(index_layout)

        tape_layout = QHBoxLayout()
        tape_layout.setSpacing(0)
        for idx in range(2 * self.window + 1):
            cell = Cell(idx, self)
            tape_layout.addWidget(cell)
            self.cells.append(cell)
        main_layout.addLayout(tape_layout)

        btn_layout = QHBoxLayout()
        btn_left = QPushButton("<-")
        btn_right = QPushButton("->")
        btn_left.setFixedSize(self.cell_size * self.window, self.cell_size)
        btn_right.setFixedSize(self.cell_size * self.window, self.cell_size)
        btn_left.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        btn_right.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        btn_left.clicked.connect(self.move_left)
        btn_right.clicked.connect(self.move_right)
        btn_layout.addWidget(btn_left)
        btn_layout.addWidget(btn_right)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(btn_layout)

        self.update_view()

    def calculate_fixed_size(self):
        width = (2 * self.window + 1) * self.cell_size
        height = self.cell_size + self.cell_size // 2 + self.cell_size * 2  # Лента + кнопки
        return width, height

    def update_view(self):
        start = self.tape.head - self.window
        for idx, lbl in enumerate(self.index_labels):
            pos = start + idx
            lbl.setText(str(pos))

        for idx, cell in enumerate(self.cells):
            pos = start + idx
            cell.blockSignals(True)
            cell.setText(self.tape.tape[pos])
            cell.blockSignals(False)
            if pos == self.tape.head:
                cell.setStyleSheet(
                    "border:2px solid red; background-color: orange; font-size: 20px;"
                )
            else:
                cell.setStyleSheet(
                    "border:1px solid black; font-size: 20px;"
                )

    def move_left(self):
        self.tape.move(Direction.LEFT)
        self.update_view()

    def move_right(self):
        self.tape.move(Direction.RIGHT)
        self.update_view()


if __name__ == '__main__':
    import sys

    from PySide6.QtWidgets import QApplication, QMainWindow


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Turing Tape Editor with Indices")
            self.tape = TuringTape("1011_001")
            self.tape_widget = TapeWidget(self.tape, window_size=5, cell_size=40)
            self.setCentralWidget(self.tape_widget)

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
