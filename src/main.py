"""Main application entry point."""

import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("MelodyTranscriber")
    app.setOrganizationName("MelodyTools")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
