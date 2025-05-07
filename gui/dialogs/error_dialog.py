from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QSizePolicy, QVBoxLayout


class ErrorDialog(QDialog):
    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ошибка")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._setup_ui(message)

    def _setup_ui(self, message: str):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        button = QPushButton("OK")
        button.clicked.connect(self.accept)
        button.setFixedWidth(100)

        layout.addWidget(label)
        layout.addSpacing(15)
        layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.setMinimumSize(400, 150)
        self.setMaximumSize(600, 400)
