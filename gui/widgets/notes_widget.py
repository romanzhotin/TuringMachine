from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit
)
from PySide6.QtCore import Qt


class NotesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        task_label = QLabel("Условие задачи:")
        self.task_edit = QTextEdit()

        comments_label = QLabel("Комментарии:")
        self.comments_edit = QTextEdit()

        layout.addWidget(task_label)
        layout.addWidget(self.task_edit)
        layout.addWidget(comments_label)
        layout.addWidget(self.comments_edit)

        self.setLayout(layout)
