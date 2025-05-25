import sys
import platform
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QStyleFactory

# HiDPI-политика должна устанавливаться ДО создания QApplication
QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)

app = QApplication(sys.argv)

# На Windows и macOS принудительно используем Fusion-стиль,
# чтобы QSS выглядело идентично Linux
system = platform.system().lower()
if system.startswith("win") or system.startswith("darwin"):
    app.setStyle(QStyleFactory.create("Fusion"))

# Путь к папке со стилями
project_root = Path(__file__).parent
styles_dir = project_root / "styles" / "light"

# Выбор QSS-файла по ОС
if system.startswith("linux"):
    qss_path = styles_dir / "linux.qss"
elif system.startswith("win"):
    qss_path = styles_dir / "windows.qss"
elif system.startswith("darwin"):
    qss_path = styles_dir / "mac.qss"
else:
    qss_path = styles_dir / "linux.qss"

# Если файл существует, читаем и применяем
if qss_path.exists():
    with open(qss_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

# Импорт и запуск главного окна
from gui.main_window import MainWindow  # noqa: E402

main_window = MainWindow()
main_window.show()

sys.exit(app.exec())
