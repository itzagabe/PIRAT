import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QCheckBox
import math

k = 15 ### CHANGE THIS IF NEEDED

saved_results = []
show_clear_confirm = True
show_remove_confirm = True

def calculate():
    input_text = inputTextBox.text()
    
    try:
        # Parse the input to extract CVE scores for each device
        devices = input_text.split('), (')
        devices = [device.replace('(', '').replace(')', '') for device in devices]
        devices = [list(map(float, device.split(','))) for device in devices]
        
        baseline_severity = 0.1
        baseline_device = 0.01
        
        V = []
        for device in devices:
            # Step 1: Normalize CVE Severities
            severity_weights = [(cve + baseline_severity) / 3.89 for cve in device]
            
            # Step 2: Calculate Adjusted Severity Sum with Diminishing Returns
            adjusted_severity_sum = math.sqrt(sum(severity_weights))
            
            # Step 3: Apply Logistic Function to Device Vulnerability Score
            V_i = adjusted_severity_sum / (1 + adjusted_severity_sum)
            V.append(V_i)
        
        # Step 4: Calculate Device Contribution
        C = [v + baseline_device for v in V]
        
        # Step 5: Calculate Overall Group Compromise Probability
        result5 = 1 - math.prod(1 - c for c in C)
        resultLabel5.setText(f"Equation 5: {result5:.2f}")

    except ValueError:
        pass


def save_result():
    input_text = inputTextBox.text()
    if input_text:
        # result1 = resultLabel1.text().split(': ')[1]
        # result2 = resultLabel2.text().split(': ')[1]
        # result3 = resultLabel3.text().split(': ')[1]
        # result4 = resultLabel4.text().split(': ')[1]
        result5 = resultLabel5.text().split(': ')[1]
        result_text = f"Input: {input_text}\nOutput: {result5}\n"
        saved_results.append(result_text)
        
        item = QListWidgetItem(result_text)
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

app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout()

inputLabel = QLabel("Enter values in the format: (#, #), (#, #, #)")
layout.addWidget(inputLabel)

inputTextBox = QLineEdit()
inputTextBox.textChanged.connect(calculate)
layout.addWidget(inputTextBox)

# resultLabel1 = QLabel("Equation 1:")
# layout.addWidget(resultLabel1)
# resultLabel2 = QLabel("Equation 2:")
# layout.addWidget(resultLabel2)
# resultLabel3 = QLabel("Equation 3:")
# layout.addWidget(resultLabel3)
# resultLabel4 = QLabel("Equation 4:")
# layout.addWidget(resultLabel4)
resultLabel5 = QLabel("Equation 5:")
layout.addWidget(resultLabel5)

buttonLayout = QHBoxLayout()
saveButton = QPushButton("Save Result")
saveButton.clicked.connect(save_result)
buttonLayout.addWidget(saveButton)

clearButton = QPushButton("Clear List")
clearButton.clicked.connect(clear_results)
buttonLayout.addWidget(clearButton)

layout.addLayout(buttonLayout)

savedListWidget = QListWidget()
savedListWidget.itemDoubleClicked.connect(remove_result)
layout.addWidget(savedListWidget)

window.setLayout(layout)
window.setWindowTitle('Probability of Exploitability')
window.setFixedSize(500, 400)
window.show()

sys.exit(app.exec())
