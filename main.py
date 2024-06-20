from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QPushButton, QLabel, QSizePolicy, QSlider
from PySide6.QtCore import Qt
import sys
from ImpactUI import setupTopRight
from ImpactUI import setupImpact
from newUI import values as severityValues
from UpdatedImportDevices import setupImportDevices
from ImportDevices import getValues

results_window = None

def create_results_window(results):
    window = QMainWindow()
    window.setWindowTitle("Results")
    window.setGeometry(100, 100, 400, 300)
    
    container = QWidget()
    layout = QVBoxLayout(container)

    label = QLabel(results)
    layout.addWidget(label)
    
    container.setLayout(layout)
    window.setCentralWidget(container)
    return window

def show_results():
    global results_window
    results = str(severityValues) + "\n"  # Replace with actual results
    results += getValues()
    results_window = create_results_window(results)
    results_window.show()

def create_main_window():
    window = QMainWindow()
    window.setWindowTitle("Main UI")

    container = QWidget()
    main_layout = QVBoxLayout(container)
    main_layout.setAlignment(Qt.AlignTop)  # Align the main layout to the top

    # Create a top frame and set up the top UI in it
    top_frame = QFrame()
    top_layout = QHBoxLayout(top_frame)

    left_container = QFrame()
    setupImportDevices(left_container)
    top_layout.addWidget(left_container)

    right_container = QFrame()
    slider1 = QSlider(Qt.Horizontal)

    setupTopRight(right_container)
    top_layout.addWidget(right_container)

    top_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    main_layout.addWidget(top_frame, alignment=Qt.AlignTop)

    # Create a bottom frame and set up the right UI in it
    bottom_frame = QFrame()
    setupImpact(bottom_frame)
    bottom_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    main_layout.addWidget(bottom_frame, alignment=Qt.AlignTop)

    # Create a button that spans the width of the main window
    print_button = QPushButton("Print Results")
    print_button.setFixedHeight(30)
    print_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    print_button.setToolTip("This button prints the results.")
    print_button.clicked.connect(show_results)

    main_layout.addWidget(print_button, alignment=Qt.AlignBottom | Qt.AlignHCenter)

    container.setLayout(main_layout)
    window.setCentralWidget(container)
    return window

def main():
    app = QApplication(sys.argv)
    window = create_main_window()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
