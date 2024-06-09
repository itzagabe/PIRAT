import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
    QFrame, QSizePolicy, QToolButton, QLabel
)
from PySide6.QtCore import Qt
from ImpactLogic import *

low = "#90EE90"  # Low
medium = "#ffd68b"  # Medium
high = "#f09d9d"  # High

values = [0, 0, 0]

def SetTooltips(widget, tooltips):
    for child in widget.findChildren(QWidget):
        if isinstance(child, QLabel):
            labelText = child.text().strip()
            if labelText in tooltips:
                child.setToolTip(tooltips[labelText])
        SetTooltips(child, tooltips)

def CreateGenericLayout(severityList, categoryList, numButtonGroups, updateFunc, defaultColor, tooltips, createResultButton):
    
    def UpdateButton(buttonGroups, activeItems, resultButton=None):
        returnValue = DisplayResults(buttonGroups, activeItems)
        updateFunc(returnValue, resultButton)

    def CreateResultButtonWidget():
        resultButton = QPushButton("")
        resultButton.setEnabled(False)
        resultButton.setStyleSheet(f"border-radius: 3px; color: black; background-color: {defaultColor};")
        resultButton.setFixedHeight(20)
        resultButton.setFixedWidth(230)
        resultButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        resultButton.setToolTip("This button shows the calculated severity value.")
        return resultButton

    def ConnectButtons(buttonGroups, activeItems, resultButton, uiFrame):
        for buttonGroupDict in buttonGroups:
            for buttonGroup in buttonGroupDict.values():
                buttonGroup.buttonToggled.connect(lambda: UpdateButton(buttonGroups, activeItems, resultButton))
        for btn in uiFrame.findChildren(QToolButton):
            btn.toggled.connect(lambda: UpdateButton(buttonGroups, activeItems, resultButton))

    mainLayout = QVBoxLayout()
    mainLayout.setSpacing(10)
    mainLayout.setContentsMargins(0, 0, 0, 0)
    
    uiFrame = QFrame()
    uiLayout = QVBoxLayout(uiFrame)
    uiLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    uiLayout.setSpacing(10)
    uiLayout.setContentsMargins(0, 0, 0, 0)
    uiFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    buttonGroups, activeItems = CreateLayout(uiLayout, severityList, categoryList, numButtonGroups)
    SetTooltips(uiFrame, tooltips)

    if createResultButton:
        resultButton = CreateResultButtonWidget()
        UpdateButton(buttonGroups, activeItems, resultButton)
        ConnectButtons(buttonGroups, activeItems, resultButton, uiFrame)
        uiLayout.addWidget(resultButton, alignment=Qt.AlignTop | Qt.AlignHCenter)
    else:
        ConnectButtons(buttonGroups, activeItems, None, uiFrame)

    return uiFrame

def UpdateImpactLayout(returnValue, resultButton):
    returnValue2 = sum(val[3] for val in returnValue) / len(returnValue) if returnValue else 0
    colors = [(0, "#bababa"), (0.3, low), (0.6, medium), (1, high)]
    
    for i in range(len(colors) - 1):
        if colors[i][0] <= returnValue2 <= colors[i + 1][0]:
            factor = (returnValue2 - colors[i][0]) / (colors[i + 1][0] - colors[i][0])
            color = InterpolateColour(colors[i][1], colors[i + 1][1], factor)
            break
    else:
        color = colors[-1][1]

    resultButton.setText(f"Average Severity: {returnValue2:.2f}")
    resultButton.setStyleSheet(f"background-color: {color}; border-radius: 3px; color: black;")
    values[0] = round(returnValue2, 2)

def UpdateDataLayout(returnValue, resultButton):
    severityLabel, severityValue = MapDataCategories(returnValue)
    colorMap = {"Very Low": "#d4f1d4", "Low": low, "Moderate": medium, "High": high, "Very High": "#f28888"}
    color = colorMap.get(severityLabel, "#FFFFFF")
    resultButton.setText(f"{severityLabel} ({severityValue})")
    resultButton.setStyleSheet(f"background-color: {color}; border-radius: 3px; color: black;")
    values[1] = severityValue
    
def UpdatePolicyLayout(returnValue, resultButton):
    values[2] = returnValue[0][3]

def ImpactCategories():
    severityList = [("None", 0, "#bababa"), ("Low", 0.3, low), ("Medium", 0.6, medium), ("High", 1, high)]
    categoryList = [
        ("Operational", ["Proprietary", "System"]), ("Safety", []), ("Financial", []),
        ("Privacy and Legislative", ["Societal Loss", "Regulatory Loss", "Environmental Loss"])
    ]
    tooltips = {
        "Operational": "Operational impact category", "Proprietary": "Operational - Proprietary subcategory",
        "System": "Operational - System subcategory", "Safety": "Safety impact category",
        "Financial": "Financial impact category", "Privacy and Legislative": "Privacy and Legislative impact category",
        "Societal Loss": "Privacy and Legislative - Societal Loss subcategory",
        "Regulatory Loss": "Privacy and Legislative - Regulatory Loss subcategory",
        "Environmental Loss": "Privacy and Legislative - Environmental Loss subcategory"
    }

    return CreateGenericLayout(severityList, categoryList, 2, UpdateImpactLayout, "#bababa", tooltips, True)

def DataCategories():
    severityList = [("Low", 1, low), ("Medium", 2, medium), ("High", 3, high)]
    tooltips = {"Data Rate": "Impact based on data rate", "Publishers": "Impact based on number of publishers"}

    return CreateGenericLayout(severityList, ['Data Rate', 'Publishers'], 1, UpdateDataLayout, "#90EE90", tooltips, True)

def PolicyCategories():
    severityList = [("None", 0, "#bababa"), ("Low", 0.3, low), ("Medium", 0.6, medium), ("High", 1, high)]
    tooltips = {"Policy Strength": "How strong are security-related procedural policies and guidelines"}

    return CreateGenericLayout(severityList, ['Policy Strength'], 1, UpdatePolicyLayout, "#bababa", tooltips, False)

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Main UI")

    impactFrame = ImpactCategories()
    dataFrame = DataCategories()
    policyFrame = PolicyCategories()
    
    mainLayout = QHBoxLayout()
    mainLayout.setSpacing(10)
    mainLayout.setContentsMargins(0, 0, 0, 0)
    mainLayout.setAlignment(Qt.AlignTop)

    leftLayout = QVBoxLayout()
    leftLayout.setSpacing(10)
    leftLayout.setAlignment(Qt.AlignTop)
    
    leftLayout.addWidget(policyFrame)
    
    dataContainer = QFrame()
    dataContainerLayout = QVBoxLayout(dataContainer)
    dataContainerLayout.setAlignment(Qt.AlignHCenter)
    dataContainerLayout.addWidget(dataFrame)
    leftLayout.addWidget(dataContainer)

    mainLayout.addLayout(leftLayout)
    mainLayout.addWidget(impactFrame)
    
    container = QWidget()
    container.setLayout(mainLayout)
    window.setCentralWidget(container)

    printButton = QPushButton("Print Values")
    printButton.setFixedHeight(30)
    printButton.setFixedWidth(100)
    printButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    printButton.setToolTip("This button prints the values list.")
    printButton.clicked.connect(lambda: print(values))
    
    mainLayout.addWidget(printButton, alignment=Qt.AlignBottom | Qt.AlignRight)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
