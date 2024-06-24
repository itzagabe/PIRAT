from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton,
    QLabel, QCheckBox, QListWidget, QFileDialog, QStyle, QStackedLayout, QMessageBox, QDialog, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QIcon
from NewLogicGroup import searchPLCInfoNVD
from nvd import getExploitabilityScoreCVE, getConfidentialityImpactCVE

search_terms = []
detailed_search = False
deviceInfoList = [] # format [(cpe name, [(cve, status), (cve, status), etc]), (cpe name, [(cve, status), (cve, status), etc])]

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
    global search_terms, deviceInfoList
    if source == "Individual":
        device_name = device_name_edit.text().strip() if device_name_edit else ""
        if not device_name:
            show_error_popup("Please fill in the device name.")
            return
        search_terms.clear()
        search_terms.append((device_name, 1))
    
    try:
        deviceInfoList = searchPLCInfoNVD(search_terms, detailed_search)  # Pass the list of search terms with counts
        deviceInfoList = [(cpe, cves) for cpe, cves in deviceInfoList]

        # Populate the results list with CPEs
        results_list.clear()
        for cpe, _ in deviceInfoList:
            results_list.addItem(cpe)
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

def showCVEPopup(cpe):
    global deviceInfoList
    def toggleCVE(cpe, cve, checked):
        for device, cves in deviceInfoList:
            if device == cpe:
                for i in range(len(cves)):
                    if cves[i][0] == cve:
                        cves[i] = (cve, checked)
    app = QApplication.instance() or QApplication([])

    dialog = QDialog()
    dialog.setWindowTitle(f"CVEs for {cpe}")

    layout = QVBoxLayout()
    dialog.setLayout(layout)

    for device, cves in deviceInfoList:
        if device == cpe:
            for cve, active in cves:
                checkbox = QCheckBox(cve.id)
                checkbox.setChecked(active)
                checkbox.toggled.connect(lambda checked, cve=cve: toggleCVE(cpe, cve, checked))
                layout.addWidget(checkbox)

    close_button = QPushButton("Close")
    close_button.setStyleSheet("background-color: #ADD8E6; border: none; color: white;")
    layout.addWidget(close_button)

    close_button.clicked.connect(dialog.accept)

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
    #results_list.setToolTip("This is the list of imported devices.")
    results_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    results_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    results_list.itemDoubleClicked.connect(lambda item: showCVEPopup(item.text()))
    return results_list

def create_individual_layout():
    individual_layout = QVBoxLayout()
    device_name_edit = QLineEdit()
    device_name_edit.setPlaceholderText("Enter Device Name")
    device_name_edit.setStyleSheet("font-style: italic;")
    individual_layout.addWidget(device_name_edit)

    results_list = create_results_list()

    search_button = QPushButton("Search")
    search_button.clicked.connect(lambda: handle_search("Individual", results_list, device_name_edit))
    individual_layout.addWidget(search_button)

    individual_layout.addLayout(create_bottom_layout())
    individual_layout.addWidget(results_list)

    return individual_layout

def create_group_layout(container = None):
    if container is None:
        container = app

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

    results_list = create_results_list()

    search_button = QPushButton("Search")
    search_button.clicked.connect(lambda: handle_search("Group", results_list))
    group_layout.addWidget(search_button)

    group_layout.addLayout(create_bottom_layout())
    group_layout.addWidget(results_list)

    return group_layout

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

def create_main_container():
    global app
    app = QApplication([])

    # Main Window
    window = QWidget()
    main_layout = QVBoxLayout()

    # Top layout with dropdown and help button
    top_layout = QHBoxLayout()

    # Dropdown for Individual and Group
    dropdown = QComboBox()
    dropdown.addItems(["Individual", "Group"])
    top_layout.addWidget(dropdown)

    # Help button
    help_button = QPushButton()
    help_button.setIcon(app.style().standardIcon(QStyle.SP_MessageBoxInformation))
    help_button.setFixedSize(20, 20)  # Adjust size
    help_button.clicked.connect(lambda: show_help_window(dropdown.currentText()))
    top_layout.addWidget(help_button)

    main_layout.addLayout(top_layout)

    # Stacked Layout for Individual and Group views
    stacked_layout = QStackedLayout()

    individual_widget = QWidget()
    individual_widget.setLayout(create_individual_layout())
    stacked_layout.addWidget(individual_widget)

    group_widget = QWidget()
    group_widget.setLayout(create_group_layout())  # Provide the path to the custom icon
    stacked_layout.addWidget(group_widget)

    def switch_view(index):
        stacked_layout.setCurrentIndex(index)

    dropdown.currentIndexChanged.connect(switch_view)
    main_layout.addLayout(stacked_layout)

    # Set main layout to window
    window.setLayout(main_layout)
    window.show()
    app.exec()


def setupImportDevices(container):
    frame = QFrame(container)
    frame.setFrameShape(QFrame.Box)
    frame.setLineWidth(1)
    
    main_layout = QVBoxLayout(frame)

    # Top layout with dropdown and help button
    top_layout = QHBoxLayout()

    # Dropdown for Individual and Group
    dropdown = QComboBox()
    dropdown.addItems(["Individual", "Group"])
    top_layout.addWidget(dropdown)

    # Help button
    help_button = QPushButton()
    help_button.setIcon(container.style().standardIcon(QStyle.SP_MessageBoxInformation))
    help_button.setFixedSize(20, 20)  # Adjust size
    help_button.clicked.connect(lambda: show_help_window(dropdown.currentText()))
    top_layout.addWidget(help_button)

    main_layout.addLayout(top_layout)

    # Stacked Layout for Individual and Group views
    stacked_layout = QStackedLayout()

    individual_widget = QWidget()
    individual_widget.setLayout(create_individual_layout())
    stacked_layout.addWidget(individual_widget)

    group_widget = QWidget()
    group_widget.setLayout(create_group_layout(container))
    stacked_layout.addWidget(group_widget)

    def switch_view(index):
        stacked_layout.setCurrentIndex(index)

    dropdown.currentIndexChanged.connect(switch_view)
    main_layout.addLayout(stacked_layout)

    container.setLayout(QVBoxLayout())
    container.layout().addWidget(frame)

def getValues():
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
    num_active_cves = len(active_cves_list)
    num_inactive_cves = len(inactive_cves_list)

    #Confidentiality(active_cves_list)
    print(f'Probability of Exploitability: {ProbabilityExploitability(active_cves_list)}')
    return f"# of CPEs: {num_cpes}, # of active CVEs: {num_active_cves}, # of inactive CVEs: {num_inactive_cves}"

def Confidentiality(cveList):
    for cpe, cves in cveList:
        print(cpe)

        for cve in cves:
            print(getConfidentialityImpactCVE(cve))

def ProbabilityExploitability(cveList):
    probabilities = []

    for cpe, cves in cveList:
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

        

def main():
    create_main_container()

if __name__ == "__main__":
    main()
