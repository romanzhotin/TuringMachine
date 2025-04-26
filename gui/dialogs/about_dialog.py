from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout
)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        self.setFixedSize(400, 400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        info_text = """
        <b>Моя Программа</b><br>
        Версия 1.0.0<br><br>

        Разработчик: Жотин Роман<br>
        """
        layout.addWidget(QLabel(info_text))

        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
