import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QCheckBox, QFileDialog, QSizePolicy, QScrollArea
import math

savedResults = []
showClearConfirm = True
showRemoveConfirm = True

def Formula3(parsedDevices):
    b_c = 0.0001
    b_d = 0.005
    c_w = 5
    
    v3 = []
    for device in parsedDevices:
        susceptability_ij = [(exploit / 3.89) ** c_w + b_c for exploit in device]
        compromise_ij = [math.sqrt(sus / (1 + sus)) for sus in susceptability_ij]
        compromisei = b_d + (1 - b_d) * (1 - math.prod(1 - comp for comp in compromise_ij))
        v3.append(compromisei)
    pVe = 1 - math.prod(1 - v for v in v3)
    return pVe, pVe * 100

def Calculate():
    inputText = inputTextBox.text()
    
    try:
        devices = inputText.split('), (')
        devices = [device.replace('(', '').replace(')', '') for device in devices]
        
        parsedDevices = []
        for device in devices:
            parsedDevice = []
            for value in device.split(','):
                try:
                    num = float(value.strip())
                    if num > 3.89:
                        raise ValueError("All CVE scores must be less than or equal to 3.89.")
                    parsedDevice.append(num)
                except ValueError:
                    if value.strip():
                        raise ValueError("Invalid input")
            parsedDevices.append(parsedDevice)
        
        result3, result3Percentage = Formula3(parsedDevices)

        resultLabel.setText(f"Formula 3: {result3:.3f} / {result3Percentage:.2f}%")

    except ValueError as e:
        resultLabel.setText(f"Error: {str(e)}")

def SaveResult():
    inputText = inputTextBox.text()
    if inputText:
        resultLines = resultLabel.text().split('\n')
        resultText = f"{resultLines[0].split(': ')[1]}"
        savedResults.append(f"Input: {inputText}\nOutput: {resultText}\n")
        
        item = QListWidgetItem(f"Input: {inputText}\nOutput: {resultText}\n")
        savedListWidget.addItem(item)

def RemoveResult():
    global showRemoveConfirm
    selectedItems = savedListWidget.selectedItems()
    
    if not selectedItems:
        return

    if showRemoveConfirm:
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
            showRemoveConfirm = False

    for item in selectedItems:
        savedResults.remove(item.text())
        savedListWidget.takeItem(savedListWidget.row(item))

def ClearResults():
    global showClearConfirm

    if savedListWidget.count() == 0:
        return
    
    if showClearConfirm:
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
            showClearConfirm = False

    savedResults.clear()
    savedListWidget.clear()

def ImportFromFile():
    fileDialog = QFileDialog()
    filePath, _ = fileDialog.getOpenFileName(window, "Open Input File", "", "Text Files (*.txt);;All Files (*)")
    
    if filePath:
        with open(filePath, 'r') as file:
            lines = file.readlines()
            for line in lines:
                inputTextBox.setText(line.strip())
                SaveResult()

app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout()

inputLabel = QLabel("Enter values in the format: (#, #), (#, #, #)")
layout.addWidget(inputLabel)

inputLayout = QHBoxLayout()
inputTextBox = QLineEdit()
inputTextBox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
inputTextBox.textChanged.connect(Calculate)
inputLayout.addWidget(inputTextBox, 5)

importButton = QPushButton("Import")
importButton.clicked.connect(ImportFromFile)
importButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
inputLayout.addWidget(importButton, 1)

layout.addLayout(inputLayout)

resultLabel = QLabel("Equation:")
layout.addWidget(resultLabel)

buttonLayout = QHBoxLayout()
saveButton = QPushButton("Save Result")
saveButton.clicked.connect(SaveResult)
buttonLayout.addWidget(saveButton)

clearButton = QPushButton("Clear List")
clearButton.clicked.connect(ClearResults)
buttonLayout.addWidget(clearButton)

layout.addLayout(buttonLayout)

scrollArea = QScrollArea()
scrollArea.setWidgetResizable(True)
savedListWidget = QListWidget()
savedListWidget.itemDoubleClicked.connect(RemoveResult)
scrollArea.setWidget(savedListWidget)

layout.addWidget(scrollArea)

window.setLayout(layout)
window.setWindowTitle('Probability of Exploitability')
window.setFixedSize(500, 800)
window.show()

sys.exit(app.exec())
