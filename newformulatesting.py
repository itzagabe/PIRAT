import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QMessageBox, QCheckBox, QFileDialog, QSizePolicy, QScrollArea
import math

savedResults = []
showClearConfirm = True
showRemoveConfirm = True

def Formula(parsedDevices):
    b_c = 0.0001
    b_d = 0.005
    c_w = 2
    
    overallResilience = 1
    for device in parsedDevices:  # i...N
        deviceResilience = 1

        for exploit, impact in device: # j...M
            if impact == 'n':
                quantizedExploit = b_c + (1 - b_c) * (0.1 * (exploit / 3.89) ** c_w)
            elif impact == 'l':
                quantizedExploit = b_c + (1 - b_c) * (0.3 * (exploit / 3.89) ** c_w)
            elif impact == 'h':
                quantizedExploit = b_c + (1 - b_c) * (1.0 * (exploit / 3.89) ** c_w)
            
            deviceResilience *= 1 - quantizedExploit
        
        deviceCompromise = b_d + (1 - b_d) * (1 - deviceResilience)
        overallResilience *= 1 - deviceCompromise

    pVe_alt = 1 - overallResilience
    return pVe_alt, pVe_alt * 100

def Formula2(parsedDevices):
    b_c = 0.0001
    b_d = 0.005
    c_w = 3
    
    overallResilience = 1
    for device in parsedDevices:  # i...N
        deviceResilience = 1

        for exploit, impact in device: # j...M
            if impact == 'n':
                quantizedExploit = b_c + (1 - b_c) * (0.1 * (exploit / 3.89) ** c_w)
            elif impact == 'l':
                quantizedExploit = b_c + (1 - b_c) * (0.3 * (exploit / 3.89) ** c_w)
            elif impact == 'h':
                if exploit == 3.89:
                    return 1, 1 * 100
                quantizedExploit = b_c + (1 - b_c) * (1.0 * (exploit / 3.89) ** c_w)
            
            logisticExploit = (quantizedExploit / (1 + quantizedExploit)) ** (1./ 3)
            deviceResilience *= 1 - quantizedExploit
        
        deviceCompromise = b_d + (1 - b_d) * (1 - deviceResilience)
        overallResilience *= 1 - deviceCompromise

    pVe_alt = 1 - overallResilience
    return pVe_alt, pVe_alt * 100

def Calculate():
    inputText = inputTextBox.text()
    
    try:
        devices = inputText.split('), (')
        devices = [device.replace('(', '').replace(')', '') for device in devices]
        
        parsedDevices = []
        for device in devices:
            parsedDevice = []
            for value in device.split(','):
                value = value.strip()
                if len(value) > 1 and value[-1] in 'nlh':
                    try:
                        num = float(value[:-1])
                        if num > 3.89:
                            raise ValueError("All CVE scores must be less than or equal to 3.89.")
                        impact = value[-1]
                        parsedDevice.append((num, impact))
                    except ValueError:
                        raise ValueError("Invalid input")
                else:
                    raise ValueError("Invalid format for impact score")
            parsedDevices.append(parsedDevice)
        
        result1 = Formula(parsedDevices)
        result2 = Formula2(parsedDevices)

        resultLabel.setText(
            f"Formula 1: {result1[0]:.3f} / {result1[1]:.2f}%\n"
            #f"Formula 2: {result2[0]:.3f} / {result2[1]:.2f}%"
        )

    except ValueError as e:
        resultLabel.setText(f"Error: {str(e)}")

def SaveResult():
    inputText = inputTextBox.text()
    if inputText:
        resultText = resultLabel.text()
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

inputLabel = QLabel("Enter values in the format: (#<impact>), (#<impact>, #<impact>) \nn = None, l = Low, h = High      i.e. 3.5h = 3.5 exploitability score, high impact")
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
