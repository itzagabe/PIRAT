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
        values = list(map(float, input_text.split(',')))
        
        M = max(values)
        O = sum(values)
        N = len(values)

        result1 = 0.9 * M + 0.1 * (1 / (1 + math.exp(-1 * (O - k))))
        resultLabel1.setText(f"Equation 1: {result1:.2f}")

        result2 = (0.9 * M + 0.1 * (O / N)) * (1 - (N - 1) / (k - 1)) + (N - 1) / (k - 1)
        resultLabel2.setText(f"Equation 2: {result2:.2f}")

        result3 = (0.9 * M + 0.1 * (O / N)) + (0.1 * (math.log(N + 1) / math.log(N + 10)))
        resultLabel3.setText(f"Equation 3: {result3:.2f}")

        if N < 5:
            R = 0.25
        elif 5 <= N < 10:
            R = 0.5
        elif 10 <= N < 20:
            R = 0.75
        else:
            R = 1.0
        result4 = 0.8 * M + 0.1 * (O / N) + 0.1 * R
        resultLabel4.setText(f"Equation 4: {result4:.2f}")

    except ValueError:
        pass

def save_result():
    input_text = inputTextBox.text()
    if input_text:
        result1 = resultLabel1.text().split(': ')[1]
        result2 = resultLabel2.text().split(': ')[1]
        result3 = resultLabel3.text().split(': ')[1]
        result4 = resultLabel4.text().split(': ')[1]
        result_text = f"Input: {input_text}\nOutput: {result1}, {result2}, {result3}, {result4}\n"
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

inputLabel = QLabel("Enter values in the format: #, #, #")
layout.addWidget(inputLabel)

inputTextBox = QLineEdit()
inputTextBox.textChanged.connect(calculate)
layout.addWidget(inputTextBox)

resultLabel1 = QLabel("Equation 1:")
layout.addWidget(resultLabel1)
resultLabel2 = QLabel("Equation 2:")
layout.addWidget(resultLabel2)
resultLabel3 = QLabel("Equation 3:")
layout.addWidget(resultLabel3)
resultLabel4 = QLabel("Equation 4:")
layout.addWidget(resultLabel4)

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
