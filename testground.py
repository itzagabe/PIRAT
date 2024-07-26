from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFrame, QPushButton, QLabel, QSizePolicy
from PySide6.QtCore import Qt
import sys
from newUI import setup_ui as SetUpBottom
from newUI import values as severityValues
from ImportDevicesUI import setup_ui as SetUpTop
from ImportDevicesUI import deviceInfoList, getImportValues

class ResultsWindow(QMainWindow):
    def __init__(self, results, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Results")
        self.setGeometry(100, 100, 400, 300)
        
        container = QWidget()
        layout = QVBoxLayout(container)

        label = QLabel(results)
        layout.addWidget(label)
        
        container.setLayout(layout)
        self.setCentralWidget(container)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main UI")
        self.results_window = None  # Hold a reference to the ResultsWindow

        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setAlignment(Qt.AlignTop)  # Align the main layout to the top

        # Create a top container and set up the top UI in it
        top_container = QFrame()
        SetUpTop(top_container)
        main_layout.addWidget(top_container, alignment=Qt.AlignTop)  # Align the top container to the top

        # Create a bottom container and set up the bottom UI in it
        bottom_container = QFrame()
        SetUpBottom(bottom_container)
        main_layout.addWidget(bottom_container, alignment=Qt.AlignTop)  # Align the bottom container to the top

        # Create a button that spans the width of the main window
        print_button = QPushButton("Print Results")
        print_button.setFixedHeight(30)
        print_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        print_button.setToolTip("This button prints the results.")
        print_button.clicked.connect(self.show_results)

        main_layout.addWidget(print_button, alignment=Qt.AlignBottom | Qt.AlignHCenter)

        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def show_results(self):
        results = str(severityValues) + "\n"  # Replace with actual results
        results += getImportValues()
        self.results_window = ResultsWindow(results)
        self.results_window.show()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
