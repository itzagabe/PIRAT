import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QCheckBox, QFileDialog, QSizePolicy, QScrollArea
import math

k = 15  # CHANGE THIS IF NEEDED

saved_results = []
show_clear_confirm = True
show_remove_confirm = True

def calculate():
    input_text = inputTextBox.text()
    
    try:
        # Parse the input to extract CVE scores for each device
        devices = input_text.split('), (')
        devices = [device.replace('(', '').replace(')', '') for device in devices]
        
        parsed_devices = []
        for device in devices:
            parsed_device = []
            for value in device.split(','):
                try:
                    num = float(value.strip())
                    if num > 3.89:
                        raise ValueError("All CVE scores must be less than or equal to 3.89.")
                    parsed_device.append(num)
                except ValueError:
                    if value.strip():  # Only raise error for non-empty invalid values
                        raise ValueError("Invalid input: could not convert string to float")
            parsed_devices.append(parsed_device)
        
        baseline_severity = 0.005  # Significantly reduced baseline severity
        baseline_device = 0.005
        weight_power1 = 3  # Increased power to emphasize higher severity scores more
        weight_power2 = 2.5 # mapped CVSS score to curve so higher ratings have higher scores

        V1 = []
        V2 = []
        for device in parsed_devices:
            
            # Step 1: Normalize CVE Severities and apply higher weight to higher severities (Formula 1)
            severity_weights1 = [((cve + baseline_severity) / 3.89) ** weight_power1 for cve in device]
            
            # Step 1: Normalize CVE Severities and apply higher weight to higher severities (Formula 2)
            severity_weights2 = [(( (((cve / 3.89) ** weight_power2) * 3.89) + baseline_severity) / 3.89) ** weight_power1 for cve in device]
            
            # Step 2: Calculate Adjusted Device Score with Cube Root (Formula 1)
            adjusted_severity_sum1 = math.pow(sum(severity_weights1), 1/weight_power1)  # Cube root for diminishing returns
            V1_i = math.sqrt(adjusted_severity_sum1 / (1 + adjusted_severity_sum1)) + baseline_device
            V1.append(V1_i)
            
            # Step 2: Calculate Adjusted Device Score with Cube Root (Formula 2)
            adjusted_severity_sum2 = math.pow(sum(severity_weights2), 1/weight_power2)  # Cube root for diminishing returns
            V2_i = math.sqrt(adjusted_severity_sum2 / (1 + adjusted_severity_sum2)) + baseline_device
            V2.append(V2_i)
        
        # Step 4: Calculate Overall Group Compromise Probability
        result1 = 1 - math.prod(1 - v for v in V1)
        result1_percentage = result1 * 100
        
        result2 = 1 - math.prod(1 - v for v in V2)
        result2_percentage = result2 * 100

        resultLabel.setText(f"Formula 1: {result1:.3f} / {result1_percentage:.2f}%\nFormula 2: {result2:.3f} / {result2_percentage:.2f}%")

    except ValueError as e:
        resultLabel.setText(f"Error: {str(e)}")

def save_result():
    input_text = inputTextBox.text()
    if input_text:
        result_lines = resultLabel.text().split('\n')
        result_text = f"{result_lines[0].split(': ')[1]} | {result_lines[1].split(': ')[1]}"
        saved_results.append(f"Input: {input_text}\nOutput: {result_text}\n")
        
        item = QListWidgetItem(f"Input: {input_text}\nOutput: {result_text}\n")
        savedListWidget.addItem(item)

def remove_result():
    global show_remove_confirm

    selected_items = savedListWidget.selectedItems()
    
    if not selected_items:
        return

    if show_remove_confirm:
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("Are you sure you want to remove the selected item(s)?")
        msgBox.setWindowTitle("Confirm Remove")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        checkBox = QCheckBox("Do not ask me again")
        msgBox.setCheckBox(checkBox)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.No:
            return
        if checkBox.isChecked():
            show_remove_confirm = False

    for item in selected_items:
        saved_results.remove(item.text())
        savedListWidget.takeItem(savedListWidget.row(item))

def clear_results():
    global show_clear_confirm

    if savedListWidget.count() == 0:
        return
    
    if show_clear_confirm:
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("Are you sure you want to clear the entire list?")
        msgBox.setWindowTitle("Confirm Clear")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        checkBox = QCheckBox("Do not ask me again")
        msgBox.setCheckBox(checkBox)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.No:
            return
        if checkBox.isChecked():
            show_clear_confirm = False

    saved_results.clear()
    savedListWidget.clear()

def import_from_file():
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(window, "Open Input File", "", "Text Files (*.txt);;All Files (*)")
    
    if file_path:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                inputTextBox.setText(line.strip())
                save_result()

app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout()

inputLabel = QLabel("Enter values in the format: (#, #), (#, #, #)")
layout.addWidget(inputLabel)

inputLayout = QHBoxLayout()
inputTextBox = QLineEdit()
inputTextBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
inputTextBox.textChanged.connect(calculate)
inputLayout.addWidget(inputTextBox, 5)

importButton = QPushButton("Import")
importButton.clicked.connect(import_from_file)
importButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
inputLayout.addWidget(importButton, 1)

layout.addLayout(inputLayout)

resultLabel = QLabel("Equation:")
layout.addWidget(resultLabel)

buttonLayout = QHBoxLayout()
saveButton = QPushButton("Save Result")
saveButton.clicked.connect(save_result)
buttonLayout.addWidget(saveButton)

clearButton = QPushButton("Clear List")
clearButton.clicked.connect(clear_results)
buttonLayout.addWidget(clearButton)

layout.addLayout(buttonLayout)

scrollArea = QScrollArea()
scrollArea.setWidgetResizable(True)
savedListWidget = QListWidget()
savedListWidget.itemDoubleClicked.connect(remove_result)
scrollArea.setWidget(savedListWidget)

layout.addWidget(scrollArea)

window.setLayout(layout)
window.setWindowTitle('Probability of Exploitability')
window.setFixedSize(500, 400)
window.show()

sys.exit(app.exec())
