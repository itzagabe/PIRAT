from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton,
    QLabel, QCheckBox, QListWidget, QFileDialog, QStyle, QStackedLayout, QMessageBox, QDialog, QFrame, QListWidgetItem, QFormLayout, QSpinBox, QToolButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QIcon
from nvd import searchPLCInfoNVD
from nvd import getExploitabilityScoreCVE, getConfidentialityImpactCVE
import math

search_terms = []
detailed_search = False
deviceInfoList = []  # format [(cpe name, [(cve, status), (cve, status), etc]), (cpe name, [(cve, status), (cve, status), etc])]
results_to_device_map = {}

def toggle_detailed_search(state):
    global detailed_search
    detailed_search = bool(state)
    print(state)

def show_error_popup(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle("Error")
    msg_box.exec()

def handle_search(source, results_list, device_name_edit=None):
    global search_terms, deviceInfoList, results_to_device_map
    if source == "Individual":
        device_name = device_name_edit.text().strip() if device_name_edit else ""
        if not device_name:
            show_error_popup("Please fill in the device name.")
            return
        search_terms.clear()
        search_terms.append((device_name, 1))
    
    try:
        # Perform search with the current search terms
        new_device_info_list = searchPLCInfoNVD(search_terms, detailed_search)  # Pass the list of search terms with counts
        new_device_info_list = [(cpe, cves) for cpe, cves in new_device_info_list]

        # Append new devices to the existing list after the search
        start_idx = len(deviceInfoList)
        deviceInfoList.extend(new_device_info_list)

        # Clear the results list before populating it with past and new devices
        results_list.clear()
        results_to_device_map.clear()

        # Populate the results list with both past and new devices
        for idx in range(len(deviceInfoList)):
            cpe, _ = deviceInfoList[idx]
            item = QListWidgetItem(cpe)
            results_list.addItem(item)
            results_to_device_map[idx] = item
    except Exception as e:
        show_error_popup(f"An error occurred during search: {e}")

def handle_group_file_load(path_box):
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(None, "Open File", "", "All Files (*)")

    if file_path:
        path_box.setText(file_path)
        path_box.setStyleSheet("")  # Reset to default style if a file is loaded
        global search_terms
        search_terms = []
        search_term_counts = {}
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if not line.startswith("#"):
                    search_term = line.strip()
                    if search_term in search_term_counts:
                        search_term_counts[search_term] += 1
                    else:
                        search_term_counts[search_term] = 1

        search_terms = [(term, count) for term, count in search_term_counts.items()]
    else:
        path_box.setPlaceholderText("File path will be displayed here")
        path_box.setStyleSheet("font-style: italic;")

def showCVEPopup(item, results_list):
    global deviceInfoList, results_to_device_map
    idx = results_list.row(item)
    cpe, cves = deviceInfoList[idx]
    
    def toggleCVE(idx, cve, checked):
        for i in range(len(deviceInfoList[idx][1])):
            if deviceInfoList[idx][1][i][0] == cve:
                deviceInfoList[idx][1][i] = (cve, checked)
                        
    def remove_device():
        reply = QMessageBox.question(
            None, 'Remove Device',
            f"Are you sure you want to remove the device {cpe}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            global deviceInfoList, results_to_device_map
            del deviceInfoList[idx]
            results_list.takeItem(idx)
            results_to_device_map.clear()
            for i in range(len(deviceInfoList)):
                results_to_device_map[i] = results_list.item(i)
            dialog.accept()

    app = QApplication.instance() or QApplication([])

    dialog = QDialog()
    dialog.setWindowTitle(f"CVEs for {cpe}")

    layout = QVBoxLayout()
    dialog.setLayout(layout)

    for cve, active in cves:
        checkbox = QCheckBox(cve.id)
        checkbox.setChecked(active)
        checkbox.toggled.connect(lambda checked, cve=cve: toggleCVE(idx, cve, checked))
        layout.addWidget(checkbox)

    button_layout = QHBoxLayout()
    
    remove_button = QPushButton("Remove")
    #remove_button.setStyleSheet("background-color: #FF6347; border: none; color: white;")
    remove_button.clicked.connect(remove_device)
    button_layout.addWidget(remove_button)
    
    close_button = QPushButton("Close")
    #close_button.setStyleSheet("background-color: #ADD8E6; border: none; color: white;")
    close_button.clicked.connect(dialog.accept)
    button_layout.addWidget(close_button)
    
    layout.addLayout(button_layout)

    dialog.exec()

def create_bottom_layout():
    bottom_layout = QHBoxLayout()
    imported_devices_label = QLabel("Imported Devices")
    imported_devices_label.setToolTip("This is the list of imported devices.")
    bottom_layout.addWidget(imported_devices_label, alignment=Qt.AlignLeft)

    detailed_search_layout = QHBoxLayout()
    detailed_search_label = QLabel("Detailed Search")
    detailed_search_label.setToolTip("Enable this for a more refined search.")
    detailed_search_checkbox = QCheckBox()
    detailed_search_checkbox.setToolTip("Enable this for a more refined search.")
    detailed_search_checkbox.stateChanged.connect(toggle_detailed_search)
    detailed_search_layout.addWidget(detailed_search_label)
    detailed_search_layout.addWidget(detailed_search_checkbox)

    bottom_layout.addLayout(detailed_search_layout)
    bottom_layout.setAlignment(detailed_search_layout, Qt.AlignRight)

    return bottom_layout

def create_results_list():
    results_list = QListWidget()
    results_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    results_list.itemDoubleClicked.connect(lambda item: showCVEPopup(item, results_list))
    return results_list

def create_individual_layout(results_list):
    individual_layout = QVBoxLayout()
    device_name_edit = QLineEdit()
    device_name_edit.setPlaceholderText("Enter Device Name")
    device_name_edit.setStyleSheet("font-style: italic;")
    individual_layout.addWidget(device_name_edit)

    search_button = QPushButton("Search")
    search_button.clicked.connect(lambda: handle_search("Individual", results_list, device_name_edit))
    individual_layout.addWidget(search_button)

    return individual_layout

def create_group_layout(container, results_list):
    group_layout = QVBoxLayout()

    group_file_layout = QHBoxLayout()
    import_file_button = QPushButton()
    import_file_button.setIcon(container.style().standardIcon(QStyle.SP_DirOpenIcon))
    import_file_button.setFixedSize(20, 20)  # Adjusted size
    group_textbox = QLineEdit()
    group_textbox.setReadOnly(True)
    group_textbox.setPlaceholderText("File path will be displayed here")
    group_textbox.setStyleSheet("font-style: italic;")
    import_file_button.clicked.connect(lambda: handle_group_file_load(group_textbox))
    group_file_layout.addWidget(import_file_button)

    group_file_layout.addWidget(group_textbox)
    group_layout.addLayout(group_file_layout)

    search_button = QPushButton("Search")
    search_button.clicked.connect(lambda: handle_search("Group", results_list))
    group_layout.addWidget(search_button)

    return group_layout

def create_manual_layout():
    manual_layout = QVBoxLayout()

    add_device_button = QPushButton("Add Device")
    add_device_button.clicked.connect(handle_add_device)
    manual_layout.addWidget(add_device_button)
    search_button = QPushButton("Search")
    search_button.setEnabled(False)
    manual_layout.addWidget(search_button)


    return manual_layout

def handle_add_device(results_list):
    app = QApplication.instance() or QApplication([])

    dialog = QDialog()
    dialog.setWindowTitle("Add Device")

    layout = QVBoxLayout()
    dialog.setLayout(layout)

    cpe_label = QLabel("Enter CPE Name:")
    cpe_name_edit = QLineEdit()
    cpe_name_edit.setPlaceholderText("Enter CPE Name")
    layout.addWidget(cpe_label)
    layout.addWidget(cpe_name_edit)

    cve_list_layout = QVBoxLayout()
    add_cve_button = QPushButton("Add CVE")
    cve_list_layout.addWidget(add_cve_button)

    cve_entries = []

    def add_cve_entry():
        form_layout = QHBoxLayout()
        cve_id_edit = QLineEdit()
        cve_id_edit.setPlaceholderText("Enter CVE ID")
        severity_spinbox = QSpinBox()
        severity_spinbox.setRange(0, 10)
        severity_spinbox.setSingleStep(1)
        remove_button = QToolButton()
        remove_button.setText("Remove")
        form_layout.addWidget(QLabel("CVE ID:"))
        form_layout.addWidget(cve_id_edit)
        form_layout.addWidget(QLabel("Severity Score:"))
        form_layout.addWidget(severity_spinbox)
        form_layout.addWidget(remove_button)
        
        cve_list_layout.addLayout(form_layout)
        cve_entries.append((form_layout, cve_id_edit, severity_spinbox, remove_button))

        def remove_cve_entry():
            cve_entries.remove((form_layout, cve_id_edit, severity_spinbox, remove_button))
            form_layout.deleteLater()

        remove_button.clicked.connect(remove_cve_entry)

    add_cve_button.clicked.connect(add_cve_entry)
    layout.addLayout(cve_list_layout)

    button_layout = QHBoxLayout()
    save_button = QPushButton("Save")
    cancel_button = QPushButton("Cancel")
    button_layout.addWidget(save_button)
    button_layout.addWidget(cancel_button)

    layout.addLayout(button_layout)

    def save_device():
        cpe_name = cpe_name_edit.text().strip()
        if not cpe_name:
            show_error_popup("Please enter a CPE name.")
            return

        cve_list = []
        for _, cve_id_edit, severity_spinbox, _ in cve_entries:
            cve_id = cve_id_edit.text().strip()
            severity = severity_spinbox.value()
            if cve_id or severity != 0:
                cve_list.append(CVE(cve_id, severity))

        deviceInfoList.append((cpe_name, [(cve, cve.metrics["cvssMetricV31"][0]["exploitabilityScore"]) for cve in cve_list]))
        
        item = QListWidgetItem(cpe_name)
        results_list.addItem(item)
        results_to_device_map[len(deviceInfoList) - 1] = item
        
        dialog.accept()

    save_button.clicked.connect(save_device)
    cancel_button.clicked.connect(dialog.reject)

    dialog.exec()

class CVE:
    def __init__(self, cve_id, exploitability_score):
        self.id = cve_id
        self.metrics = {
            "cvssMetricV31": [
                {"exploitabilityScore": exploitability_score}
            ]
        }

def create_manual_layout(results_list):
    manual_layout = QVBoxLayout()

    add_device_button = QPushButton("Add Device")
    add_device_button.clicked.connect(lambda: handle_add_device(results_list))
    manual_layout.addWidget(add_device_button)

    search_button = QPushButton("Search")
    search_button.setEnabled(False)
    manual_layout.addWidget(search_button)

    return manual_layout


def setupImportDevices(container):
    frame = QFrame(container)
    frame.setFrameShape(QFrame.Box)
    frame.setLineWidth(1)
    
    main_layout = QVBoxLayout(frame)

def clear_devices(results_list):
    reply = QMessageBox.question(
        None, 'Clear All Devices',
        "Are you sure you want to clear all devices?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )
    if reply == QMessageBox.Yes:
        global deviceInfoList, results_to_device_map
        deviceInfoList.clear()
        results_to_device_map.clear()
        results_list.clear()

def setupImportDevices(container):
    frame = QFrame(container)
    frame.setFrameShape(QFrame.Box)
    frame.setLineWidth(1)
    
    main_layout = QVBoxLayout(frame)

    # Top layout with dropdown and help button
    top_layout = QHBoxLayout()

    # Dropdown for Individual, Group, and Manual
    dropdown = QComboBox()
    dropdown.addItems(["Individual", "Group", "Manual"])  # Added "Manual"
    top_layout.addWidget(dropdown)

    # Help button
    help_button = QPushButton()
    help_button.setIcon(container.style().standardIcon(QStyle.SP_MessageBoxInformation))
    help_button.setFixedSize(20, 20)  # Adjust size
    help_button.clicked.connect(lambda: show_help_window(dropdown.currentText()))
    top_layout.addWidget(help_button)

    main_layout.addLayout(top_layout)

    # Stacked Layout for Individual, Group, and Manual views
    stacked_layout = QStackedLayout()

    results_list = create_results_list()

    individual_widget = QWidget()
    individual_layout = create_individual_layout(results_list)
    individual_widget.setLayout(individual_layout)
    stacked_layout.addWidget(individual_widget)

    group_widget = QWidget()
    group_layout = create_group_layout(container, results_list)
    group_widget.setLayout(group_layout)
    stacked_layout.addWidget(group_widget)
    
    manual_widget = QWidget()
    manual_layout = create_manual_layout(results_list)
    manual_widget.setLayout(manual_layout)
    stacked_layout.addWidget(manual_widget)

    def switch_view(index):
        stacked_layout.setCurrentIndex(index)
        #search_button.setEnabled(dropdown.currentText() != "Manual")

    dropdown.currentIndexChanged.connect(switch_view)
    main_layout.addLayout(stacked_layout)

    main_layout.addLayout(create_bottom_layout())
    main_layout.addWidget(results_list)

    clear_devices_button = QPushButton("Clear Devices")
    clear_devices_button.clicked.connect(lambda: clear_devices(results_list))
    main_layout.addWidget(clear_devices_button)

    container.setLayout(QVBoxLayout())
    container.layout().addWidget(frame)

def show_help_window(selection):
    help_text = {
        "Individual": """
1. Enter the name of the device in the entry field provided. For more accurate results, you can use the <a href='https://nvd.nist.gov/products/cpe/search'>NVD CPE database</a> to find the exact model name.<br><br>
2. Search for the device. By default, the result will be first found match. For a more refined search, use the <i>Detailed Search</i> checkbox. This will allow you to navigate a list of all potential matches for the given device name.<br>
&nbsp;&nbsp;&nbsp;&nbsp;a. If too many potential matches are found, you will be asked to provide more detail and try again.<br>
&nbsp;&nbsp;&nbsp;&nbsp;b. If no matches are found, you will be asked to redefine your search.<br>
<b>NOTE:</b> <i>Detailed Search is only recommended for advanced users.</i><br><br>
3. After a successful search, the <i>Imported Devices</i> dropdown will be populated with the found device. Double click the entry to modify its CVEs.<br>
&nbsp;&nbsp;&nbsp;&nbsp;a. By default, all CVEs less than 10 years old are enabled.<br>
&nbsp;&nbsp;&nbsp;&nbsp;b. Unchecking CVE checkboxes assumes the device has been "patched" and removes it from the final calculation.
        """,
        "Group": """
1. Before using this program, compile a list of devices in a text file. For more accurate results, you can use the <a href='https://nvd.nist.gov/products/cpe/search'>NVD CPE database</a> to find the exact model name.<br>
&nbsp;&nbsp;&nbsp;&nbsp;a. Place each device on a separate line.<br>
&nbsp;&nbsp;&nbsp;&nbsp;b. Lines that begin with "#" will not be read.<br><br>
2. Search for the devices. By default, the result will be first found match. For a more refined search, use the <i>Detailed Search</i> checkbox. This will allow you to navigate a list of all potential matches for the given device name.<br>
&nbsp;&nbsp;&nbsp;&nbsp;a. If too many potential matches are found, you will be asked to provide more detail and try again.<br>
&nbsp;&nbsp;&nbsp;&nbsp;b. If no matches are found, you will be asked to redefine your search.<br>
&nbsp;&nbsp;&nbsp;&nbsp;c. In the event of a detailed search, information is provided on your progress through the list and the number of repeat devices on the list.<br>
<b>NOTE:</b> <i>Detailed Search is only recommended for advanced users.</i><br><br>
3. After a successful search, the <i>Imported Devices</i> dropdown will be populated with the found device. Double click the entry to modify its CVEs.<br>
&nbsp;&nbsp;&nbsp;&nbsp;a. By default, all CVEs less than 10 years old are enabled.<br>
&nbsp;&nbsp;&nbsp;&nbsp;b. Unchecking CVE checkboxes assumes the device has been "patched" and removes it from the final calculation.
        """
    }

    app = QApplication.instance() or QApplication([])

    dialog = QDialog()
    dialog.setWindowTitle("Help")

    layout = QVBoxLayout()
    dialog.setLayout(layout)

    # Title
    title = "Individual Search" if selection == "Individual" else "Group Search"
    title_label = QLabel(title)
    title_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(title_label)

    # Line under the title
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    layout.addWidget(line)

    # Help text
    help_label = QLabel()
    help_label.setTextFormat(Qt.RichText)
    help_label.setText(help_text.get(selection, "No help available for this selection."))
    help_label.setOpenExternalLinks(True)
    help_label.setWordWrap(True)  # Ensure the text wraps within the window
    layout.addWidget(help_label)

    close_button = QPushButton("Close")
    close_button.setStyleSheet("background-color: #ADD8E6; border: none; color: white;")
    layout.addWidget(close_button)

    close_button.clicked.connect(dialog.accept)

    dialog.exec()

def getImportValues2():
    if not deviceInfoList:
        return 0, False
    # Initialize lists for active and inactive CVEs in the desired format
    active_cves_list = []
    inactive_cves_list = []

    # Iterate through the deviceInfoList
    for cpe, cves in deviceInfoList:
        active_cves = []
        inactive_cves = []
        for cve, active in cves:
            if active:
                active_cves.append(cve)
            else:
                inactive_cves.append(cve)
        
        if active_cves:
            active_cves_list.append((cpe, active_cves))
        if inactive_cves:
            inactive_cves_list.append((cpe, inactive_cves))

    # Calculate the number of CPEs, active CVEs, and inactive CVEs
    num_cpes = len(deviceInfoList)

    averageProbability = 0
    for cpe, probability in ProbabilityExploitability(active_cves_list):
    #for cpe in ProbabilityExploitability(tempCVELIST):
        averageProbability += probability
        #print(probability)
    averageProbability = averageProbability / num_cpes
    k = 5
    overallProbability = (averageProbability - (num_cpes - 1) / (k - 1)) + (num_cpes - 1) / (k - 1)
    print(f'Overall Probability = {averageProbability}\n')
    return overallProbability, True
    #return f"# of CPEs: {num_cpes}, # of active CVEs: {num_active_cves}, # of inactive CVEs: {num_inactive_cves}", deviceInfoList

def getImportValues():
    

    #UNCOMMENT#############################################################################################
    if not deviceInfoList:
        return 0, False
    #############################################################################################TEMP

    # Initialize lists for active and inactive CVEs in the desired format
    active_cves_list = []
    inactive_cves_list = []

    # Iterate through the deviceInfoList
    for cpe, cves in deviceInfoList:
        active_cves = []
        inactive_cves = []
        for cve, active in cves:
            if active:
                active_cves.append(cve)
            else:
                inactive_cves.append(cve)
        
        if active_cves:
            active_cves_list.append((cpe, active_cves))
        if inactive_cves:
            inactive_cves_list.append((cpe, inactive_cves))

    baseline_severity = 0.1
    baseline_device = 0.05
    
    vulnerability = []
    
    for device in active_cves_list: ## CHANGE TO active_cves_list/tempDeviceList #############################################################################################
        #print(f'ADFESF CPE {cpe}, CVE {cve}, EXPLOIT: {getExploitabilityScoreCVETEST(cve)}')
        cpe, cves = device
        #print(cve.metrics['cvssMetricV31'][0]['exploitabilityScore'])

        # Step 1: Normalize CVE Severities
        #######################-------------------######@!#@#%#$YGERGHE%RY
        #severity_ij = [min(1,(cve.metrics['cvssMetricV31'][0]['exploitabilityScore'] + baseline_severity) / 3.89) for cve in cves]
        severity_ij = [min(1,(getExploitabilityScoreCVETEST(cve) + baseline_severity) / 3.89) for cve in cves]
        #######################-------------------######@!#@#%#$YGERGHE%RY

        # Step 2: Calculate Adjusted Severity Sum with Diminishing Returns
        severity_i = math.sqrt(sum(severity_ij))
        
        # Step 3: Apply Logistic Function to Device Vulnerability Score
        vulnerability_i = severity_i / (1 + severity_i)
        vulnerability.append(vulnerability_i)
    
    # Step 4: Calculate Device Contribution
    compromise_i = [min(1, v + baseline_device) for v in vulnerability]
    
    # Step 5: Calculate Overall Group Compromise Probability
    overallProbability = 1 - math.prod(1 - c for c in compromise_i)
    print(f'Probability: {overallProbability}')

    return overallProbability, True
    #return f"# of CPEs: {num_cpes}, # of active CVEs: {num_active_cves}, # of inactive CVEs: {num_inactive_cves}", deviceInfoList

###########################################################################################
## TEST ###################################################################################
###########################################################################################
cve_scores = {
    "cve1": 3.89,
    "cve2": 1.0,
    "cve3": 1.0,
}

def getExploitabilityScoreCVETEST(cve):
    return cve_scores.get(cve, 0)

def updateCveScores(new_scores):
    global cve_scores
    cve_scores = new_scores

tempDeviceList = [
    ("cpe1", ["cve1", "cve2"]),
    ("cpe2", ["cve3"])
]

###########################################################################################
## TEST ###################################################################################
###########################################################################################


def Confidentiality(cveList):
    for cpe, cves in cveList:
        print(cpe)

        for cve in cves:
            print(getConfidentialityImpactCVE(cve))

def ProbabilityExploitability(cveList):
    probabilities = []

    for cpe, cves in cveList:
        #print(cpe, cve)
        overallScore = 0
        maxScore = 0
        for cve in cves:
            explotability = (getExploitabilityScoreCVE(cve) / 3.9)
            overallScore += explotability
            maxScore = max(maxScore, explotability)
        
        if len(cves) > 0:
            probability = (0.9 * maxScore) + (0.1 * (overallScore / len(cves)))
        else:
            probability = 0
        probabilities.append((cpe, probability))

    return probabilities
