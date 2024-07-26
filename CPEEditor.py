import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, 
    QLineEdit, QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt

from ImportDevicesUI import cve_scores, tempDeviceList, updateCveScores, getExploitabilityScoreCVETEST

class CPEEditor(QDialog):
    def __init__(self, devices, parent=None):
        super().__init__(parent)
        self.devices = devices
        self.selected_cpe = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("CPE and CVE Editor")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout(self)

        self.cpe_list = QListWidget(self)
        self.cve_list = QListWidget(self)
        
        self.updateCpeList()
        self.updateCveList()
        
        self.cpe_list.itemClicked.connect(self.cpeSelected)
        self.cve_list.itemDoubleClicked.connect(self.editCveScore)

        add_cpe_button = QPushButton("Add CPE")
        remove_cpe_button = QPushButton("Remove CPE")
        add_cve_button = QPushButton("Add CVE")
        remove_cve_button = QPushButton("Remove CVE")

        add_cpe_button.clicked.connect(self.addCpe)
        remove_cpe_button.clicked.connect(self.removeCpe)
        add_cve_button.clicked.connect(self.addCve)
        remove_cve_button.clicked.connect(self.removeCve)

        cpe_layout = QVBoxLayout()
        cpe_layout.addWidget(self.cpe_list)
        cpe_layout.addWidget(add_cpe_button)
        cpe_layout.addWidget(remove_cpe_button)

        cve_layout = QVBoxLayout()
        cve_layout.addWidget(self.cve_list)
        cve_layout.addWidget(add_cve_button)
        cve_layout.addWidget(remove_cve_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(cpe_layout)
        main_layout.addLayout(cve_layout)

        layout.addLayout(main_layout)
        
        self.setLayout(layout)

    def updateCpeList(self):
        self.cpe_list.clear()
        for cpe, cves in self.devices:
            self.cpe_list.addItem(cpe)

    def updateCveList(self):
        self.cve_list.clear()
        if self.selected_cpe:
            for cpe, cves in self.devices:
                if cpe == self.selected_cpe:
                    for cve in cves:
                        score = cve_scores.get(cve, 0)
                        self.cve_list.addItem(f"{cve}: {score}")

    def cpeSelected(self, item):
        self.selected_cpe = item.text()
        self.updateCveList()

    def addCpe(self):
        text, ok = QInputDialog.getText(self, 'Add CPE', 'Enter CPE name:')
        if ok and text:
            if any(cpe == text for cpe, cves in self.devices):
                QMessageBox.warning(self, "Duplicate CPE", "A CPE with this name already exists.")
                return
            self.devices.append((text, []))
            self.updateCpeList()

    def removeCpe(self):
        selected_items = self.cpe_list.selectedItems()
        if selected_items:
            for item in selected_items:
                cpe_name = item.text()
                for device in self.devices:
                    if device[0] == cpe_name:
                        for cve in device[1]:
                            if cve in cve_scores:
                                del cve_scores[cve]
                        self.devices.remove(device)
                        break
                if self.selected_cpe == cpe_name:
                    self.selected_cpe = None
            self.updateCpeList()
            self.updateCveList()

    def addCve(self):
        if not self.selected_cpe:
            QMessageBox.warning(self, "Warning", "Please select a CPE first.")
            return
        text, ok = QInputDialog.getText(self, 'Add CVE', 'Enter CVE name:')
        if ok and text:
            if text in cve_scores:
                QMessageBox.warning(self, "Duplicate CVE", "A CVE with this name already exists.")
                return
            score, ok = QInputDialog.getDouble(self, 'Add CVE Score', 'Enter CVE score:')
            if ok:
                if score > 3.89:
                    QMessageBox.warning(self, "Invalid Score", "The CVE score must be less than or equal to 3.89.")
                    return
                cve_scores[text] = score
                for i, (cpe, cves) in enumerate(self.devices):
                    if cpe == self.selected_cpe:
                        self.devices[i][1].append(text)
                        break
                self.updateCveList()

    def removeCve(self):
        selected_items = self.cve_list.selectedItems()
        if selected_items:
            for item in selected_items:
                cve_name = item.text().split(":")[0]
                if cve_name in cve_scores:
                    del cve_scores[cve_name]
                for i, (cpe, cves) in enumerate(self.devices):
                    if cpe == self.selected_cpe and cve_name in cves:
                        self.devices[i][1].remove(cve_name)
                        break
            self.updateCveList()

    def editCveScore(self, item):
        cve_name = item.text().split(":")[0]
        score, ok = QInputDialog.getDouble(self, 'Edit CVE Score', f'Enter new score for {cve_name}:')
        if ok:
            if score > 3.89:
                QMessageBox.warning(self, "Invalid Score", "The CVE score must be less than or equal to 3.89.")
                return
            cve_scores[cve_name] = score
            self.updateCveList()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    devices = [("CPE1", ["CVE-001", "CVE-002"]), ("CPE2", ["CVE-003"])]
    editor = CPEEditor(devices)
    editor.show()
    sys.exit(app.exec())
