import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QComboBox, QMessageBox, QFrame, QFileDialog, QListWidget, QCheckBox, QDialog
)
from PySide6.QtCore import Qt
from NewLogicGroup import *

# Define size variables
DROPDOWN_WIDTH = 100
BUTTON_WIDTH = 100
ENTRY_BOX_WIDTH = 350
RESULT_BOX_WIDTH = 350
ELEMENT_HEIGHT = 30
SPACING = 10
MAIN_WINDOW_WIDTH = 700
MAIN_WINDOW_HEIGHT = 100
MARGIN = 10


deviceInfoList = []

def dropdown_changed(dropdown, individual_widgets, group_widgets, result_list_individual, result_list_group):
    result_list_individual.clear()
    result_list_group.clear()

    if dropdown.currentText() == "Individual":
        for widget in group_widgets:
            widget.hide()
        for widget in individual_widgets:
            widget.show()
        
        if deviceInfoList and deviceInfoList[0][-1] == "individual":
            result_list_individual.clear()
            for cpe, _, _ in deviceInfoList:
                result_list_individual.addItem(cpe)
    else:
        for widget in individual_widgets:
            widget.hide()
        for widget in group_widgets:
            widget.show()

        if deviceInfoList and deviceInfoList[0][-1] == "group":
            result_list_group.clear()
            for cpe, _, _ in deviceInfoList:
                result_list_group.addItem(cpe)

def import_button_clicked(entry_box, result_list):
    global deviceInfoList

    if not entry_box.text():
        show_error_message("Entry box cannot be empty.")
    else:
        search_term = entry_box.text()
        deviceInfoList = searchPLCInfoNVD([(search_term, 1)])
        deviceInfoList = [(cpe, cves, "individual") for cpe, cves in deviceInfoList]
        result_list.clear()
        for cpe, _, _ in deviceInfoList:
            result_list.addItem(cpe)

def load_button_clicked(path_box, list_widget):
    global deviceInfoList
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(None, "Open File", "", "All Files (*)")

    if file_path:
        path_box.setText(file_path)
        search_terms = []
        search_term_counts = {}
        with open(file_path, 'r') as file:
            lines = file.readlines()
            list_widget.clear()
            for line in lines:
                if not line.startswith("#"):
                    search_term = line.strip()
                    if search_term in search_term_counts:
                        search_term_counts[search_term] += 1
                    else:
                        search_term_counts[search_term] = 1

        search_terms = [(term, count) for term, count in search_term_counts.items()]
        deviceInfoList = searchPLCInfoNVD(search_terms)  # Pass the list of search terms with counts
        deviceInfoList = [(cpe, cves, "group") for cpe, cves in deviceInfoList]

        # Populate the group result list with CPEs
        list_widget.clear()
        for cpe, _, _ in deviceInfoList:
            list_widget.addItem(cpe)

def show_error_message(message):
    error_msg = QMessageBox()
    error_msg.setIcon(QMessageBox.Critical)
    error_msg.setText(message)
    error_msg.setWindowTitle("Error")
    error_msg.exec()

def entry_box_changed(entry_box):
    entry_box.setStyleSheet("color: black; font-style: normal;")

def create_individual_widgets(inner_layout):
    import_button = QPushButton("Import")
    import_button.setFixedSize(BUTTON_WIDTH, ELEMENT_HEIGHT)
    import_button.setStyleSheet("background-color: #ADD8E6; font-size: 14px; padding: 5px; border: none;")
    inner_layout.addWidget(import_button)

    entry_box = QLineEdit()
    entry_box.setFixedSize(ENTRY_BOX_WIDTH, ELEMENT_HEIGHT)
    entry_box.setPlaceholderText("Enter Device Name")
    entry_box.setStyleSheet("color: grey; font-style: italic; font-size: 14px; padding: 5px;")
    inner_layout.addWidget(entry_box)

    result_list = QListWidget()
    result_list.setFixedSize(RESULT_BOX_WIDTH, ELEMENT_HEIGHT)
    result_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    result_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    inner_layout.addWidget(result_list)

    individual_widgets = [import_button, entry_box, result_list]

    import_button.clicked.connect(lambda: import_button_clicked(entry_box, result_list))
    entry_box.textChanged.connect(lambda: entry_box_changed(entry_box))
    result_list.itemDoubleClicked.connect(lambda item: showCVEPopup(item.text()))

    return individual_widgets

def create_group_widgets(inner_layout):
    load_button = QPushButton("Load")
    load_button.setFixedSize(BUTTON_WIDTH, ELEMENT_HEIGHT)
    load_button.setStyleSheet("background-color: #ADD8E6; font-size: 14px; padding: 5px; border: none;")
    inner_layout.addWidget(load_button)

    path_box = QLineEdit()
    path_box.setFixedSize(ENTRY_BOX_WIDTH, ELEMENT_HEIGHT)
    path_box.setReadOnly(True)
    path_box.setStyleSheet("font-size: 14px; padding: 5px;")
    inner_layout.addWidget(path_box)

    list_widget = QListWidget()
    list_widget.setFixedSize(RESULT_BOX_WIDTH, ELEMENT_HEIGHT)
    list_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    inner_layout.addWidget(list_widget)

    group_widgets = [load_button, path_box, list_widget]

    load_button.clicked.connect(lambda: load_button_clicked(path_box, list_widget))
    list_widget.itemDoubleClicked.connect(lambda item: showCVEPopup(item.text()))

    return group_widgets

def showCVEPopup(cpe):
    app = QApplication.instance() or QApplication([])

    dialog = QDialog()
    dialog.setWindowTitle(f"CVEs for {cpe}")

    layout = QVBoxLayout()
    dialog.setLayout(layout)

    for device, cves, _ in deviceInfoList:
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

def toggleCVE(cpe, cve, checked):
    for device, cves, _ in deviceInfoList:
        if device == cpe:
            for i in range(len(cves)):
                if cves[i][0] == cve:
                    cves[i] = (cve, checked)

def printSummary():
    num_cpes = len(deviceInfoList)
    num_active_cves = sum(len([cve for cve, active in cves if active]) for _, cves, _ in deviceInfoList)
    num_inactive_cves = sum(len([cve for cve, active in cves if not active]) for _, cves, _ in deviceInfoList)
    print(f"# of CPEs: {num_cpes}, # of active CVEs: {num_active_cves}, # of inactive CVEs: {num_inactive_cves}")

def getValues():
    num_cpes = len(deviceInfoList)
    num_active_cves = sum(len([cve for cve, active in cves if active]) for _, cves, _ in deviceInfoList)
    num_inactive_cves = sum(len([cve for cve, active in cves if not active]) for _, cves, _ in deviceInfoList)
    return f"# of CPEs: {num_cpes}, # of active CVEs: {num_active_cves}, # of inactive CVEs: {num_inactive_cves}"

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("PySide Example")

    # Main container
    main_container = QWidget()
    main_layout = QVBoxLayout(main_container)
    main_layout.setSpacing(SPACING)
    main_layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)

    # Top UI container
    top_container = QFrame()
    top_layout = QVBoxLayout(top_container)
    top_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    top_layout.setSpacing(SPACING)
    top_layout.setContentsMargins(0, 0, 0, 0)

    # Inner UI container
    inner_container = QFrame()
    inner_layout = QHBoxLayout(inner_container)
    inner_layout.setSpacing(SPACING)
    inner_layout.setContentsMargins(0, 0, 0, 0)

    # Dropdown menu
    dropdown = QComboBox()
    dropdown.addItems(["Individual", "Group"])
    dropdown.setFixedSize(DROPDOWN_WIDTH, ELEMENT_HEIGHT)
    dropdown.setStyleSheet("font-size: 14px; padding: 5px;")
    inner_layout.addWidget(dropdown)

    # Vertical line
    vertical_line = QFrame()
    vertical_line.setFrameShape(QFrame.VLine)
    vertical_line.setStyleSheet("background-color: grey;")
    vertical_line.setFixedHeight(ELEMENT_HEIGHT)
    inner_layout.addWidget(vertical_line)

    # Create individual and group widgets
    individual_widgets = create_individual_widgets(inner_layout)
    group_widgets = create_group_widgets(inner_layout)

    # Initially hide group widgets
    for widget in group_widgets:
        widget.hide()

    # Connect signals and slots
    dropdown.currentIndexChanged.connect(lambda: dropdown_changed(dropdown, individual_widgets, group_widgets, individual_widgets[-1], group_widgets[-1]))

    # Add inner container to top layout
    top_layout.addWidget(inner_container)

    # Horizontal line
    horizontal_line = QFrame()
    horizontal_line.setFrameShape(QFrame.HLine)
    horizontal_line.setStyleSheet("background-color: grey;")
    horizontal_line.setFixedHeight(2)
    top_layout.addWidget(horizontal_line)

    # Button to print summary
    summary_button = QPushButton("Print Summary")
    summary_button.setFixedSize(BUTTON_WIDTH, ELEMENT_HEIGHT)
    summary_button.setStyleSheet("background-color: #ADD8E6; font-size: 14px; padding: 5px; border: none;")
    summary_button.clicked.connect(printSummary)

    # Summary button container
    summary_container = QFrame()
    summary_layout = QVBoxLayout(summary_container)
    summary_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    summary_layout.setSpacing(SPACING)
    summary_layout.setContentsMargins(0, 0, 0, 0)
    summary_layout.addWidget(summary_button)

    main_layout.addWidget(top_container, alignment=Qt.AlignTop | Qt.AlignLeft)
    main_layout.addWidget(summary_container, alignment=Qt.AlignTop | Qt.AlignLeft)

    window.setCentralWidget(main_container)
    window.show()
    sys.exit(app.exec())

def setup_ui(container):
    main_layout = QVBoxLayout(container)
    main_layout.setSpacing(SPACING)
    main_layout.setContentsMargins(MARGIN, MARGIN, MARGIN, MARGIN)

    # Top UI container
    top_container = QFrame()
    top_layout = QVBoxLayout(top_container)
    top_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    top_layout.setSpacing(SPACING)
    top_layout.setContentsMargins(0, 0, 0, 0)

    # Inner UI container
    inner_container = QFrame()
    inner_layout = QHBoxLayout(inner_container)
    inner_layout.setSpacing(SPACING)
    inner_layout.setContentsMargins(0, 0, 0, 0)

    # Dropdown menu
    dropdown = QComboBox()
    dropdown.addItems(["Individual", "Group"])
    dropdown.setFixedSize(DROPDOWN_WIDTH, ELEMENT_HEIGHT)
    dropdown.setStyleSheet("font-size: 14px; padding: 5px;")
    inner_layout.addWidget(dropdown)

    # Vertical line
    vertical_line = QFrame()
    vertical_line.setFrameShape(QFrame.VLine)
    vertical_line.setStyleSheet("background-color: grey;")
    vertical_line.setFixedHeight(ELEMENT_HEIGHT)
    inner_layout.addWidget(vertical_line)

    # Create individual and group widgets
    individual_widgets = create_individual_widgets(inner_layout)
    group_widgets = create_group_widgets(inner_layout)

    # Initially hide group widgets
    for widget in group_widgets:
        widget.hide()

    # Connect signals and slots
    dropdown.currentIndexChanged.connect(
        lambda: dropdown_changed(dropdown, individual_widgets, group_widgets, individual_widgets[-1], group_widgets[-1])
    )

    # Add inner container to top layout
    top_layout.addWidget(inner_container)

    # Horizontal line
    horizontal_line = QFrame()
    horizontal_line.setFrameShape(QFrame.HLine)
    horizontal_line.setStyleSheet("background-color: grey;")
    horizontal_line.setFixedHeight(2)
    top_layout.addWidget(horizontal_line)

    # # Button to print summary
    # summary_button = QPushButton("Print Summary")
    # summary_button.setFixedSize(BUTTON_WIDTH, ELEMENT_HEIGHT)
    # summary_button.setStyleSheet("background-color: #ADD8E6; font-size: 14px; padding: 5px; border: none;")
    # summary_button.clicked.connect(printSummary)

    # # Summary button container
    # summary_container = QFrame()
    # summary_layout = QVBoxLayout(summary_container)
    # summary_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    # summary_layout.setSpacing(SPACING)
    # summary_layout.setContentsMargins(0, 0, 0, 0)
    # summary_layout.addWidget(summary_button)

    main_layout.addWidget(top_container, alignment=Qt.AlignTop | Qt.AlignLeft)
    # main_layout.addWidget(summary_container, alignment=Qt.AlignTop | Qt.AlignLeft)

if __name__ == "__main__":
    main()
