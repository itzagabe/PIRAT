import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFrame
from PySide6.QtCore import Qt
from ImpactLogic import initialize_layout, display_results

def ImpactCategories():
    def on_calculate(button_groups, active_items):
        button_groups_1, button_groups_2 = button_groups
        display_results(button_groups_1, button_groups_2, active_items)
    # Create the main layout
    main_layout = QVBoxLayout()
    
    # Create the Calculate button
    calculate_button = QPushButton("Calculate")
    
    # Create a frame to hold the UI layout
    ui_frame = QFrame()
    ui_layout = QVBoxLayout(ui_frame)
    ui_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    
    # Initialize the layout and get the button groups and active items
    button_groups, active_items = initialize_layout(ui_layout)
    
    # Connect the Calculate button to the display results function
    calculate_button.clicked.connect(lambda: on_calculate(button_groups, active_items))
    
    # Add the UI frame and Calculate button to the main layout
    main_layout.addWidget(ui_frame)
    main_layout.addWidget(calculate_button)
    
    # Return the main layout and the necessary elements
    return main_layout, button_groups, active_items

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Main UI")

    # Setup the impact logic frame
    main_layout, button_groups, active_items = ImpactCategories()
    
    # Create a container widget and set its layout
    container = QWidget()
    container.setLayout(main_layout)
    window.setCentralWidget(container)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
