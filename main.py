import sys
from PyQt6.QtWidgets import QApplication
from src.ui.window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NovaBrowse")
    app.setOrganizationName("NovaLabs")
    app.setOrganizationDomain("novalabs.ai")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
