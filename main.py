from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QPushButton, QLabel, QSizePolicy, QSlider, QLineEdit, QMessageBox
from PySide6.QtCore import Qt
import sys
from ImpactUI import setupTopRight, setupImpact, updateTimeDifference
from ImpactUI import values as IE_TI_ProSucc
from ImpactUI import timeDifference
from ImportDevices import setupImportDevices, getImportValues

results_window = None
results_text_box = None

def EmptyImport(variable):
    if not variable:
        reply = QMessageBox.question(
            None, 
            'No Imported Devices',
            f"Without any imported devices, the calculation will assume the worst case scenario in which the probability of an exploit is guaranteed. Do you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
    return True


def show_results():
    deviceProbability, isNotEmpty = getImportValues()
    if not EmptyImport(isNotEmpty):
      return
        
    def displayTimeDifference(hours):
        months = hours // (30 * 24)
        hours %= (30 * 24)
        days = hours // 24
        hours %= 24
        minutes = (hours - int(hours)) * 60
        hours = int(hours)

        result = []
        if months > 0:
            result.append(f"{months} month{'s' if months > 1 else ''}")
        if days > 0 or (months > 0 and (hours > 0 or minutes > 0)):
            result.append(f"{days} day{'s' if days > 1 else ''}")
        if hours > 0 or (days > 0 or months > 0) and minutes > 0:
            result.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0 or hours > 0 or days > 0 or months > 0:
            result.append(f"{int(minutes)} minute{'s' if int(minutes) != 1 else ''}")

        return ", ".join(result)

    if isNotEmpty:
        print('not empty')
    probability = IE_TI_ProSucc[2]
    impact = (1 - IE_TI_ProSucc[0] * IE_TI_ProSucc[1])
    finalRisk = probability * impact
    timeRange1, timeRange2 = updateTimeDifference()

    cryptoperiod = timeRange1 + (finalRisk * (timeRange2 - timeRange1))
    cryptoperiod_display = displayTimeDifference(cryptoperiod)

    #getValues()
    print(f'Probability of risk: {round(probability, 2)}')
    print(f'Impact: {round(impact, 2)}')
    print(f'Final Risk: {round(finalRisk, 2)}')
    print(f'Recommended cryptoperiod: {cryptoperiod_display}\n')

    if results_text_box:
        results_text_box.setText(f"Recommended cryptoperiod: {cryptoperiod_display}")

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

    # Create a horizontal layout for the print button and text box
    button_text_layout = QHBoxLayout()

    # Create the print button
    print_button = QPushButton("Print Results")
    print_button.setFixedHeight(30)
    print_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    print_button.setToolTip("This button prints the results.")
    print_button.clicked.connect(show_results)
    button_text_layout.addWidget(print_button, 1)

    # Create the uneditable text box
    global results_text_box
    results_text_box = QLineEdit()
    results_text_box.setReadOnly(True)
    results_text_box.setFixedHeight(30)
    results_text_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    button_text_layout.addWidget(results_text_box, 5)

    # Add the horizontal layout to the main layout
    main_layout.addLayout(button_text_layout)

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
