from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton,
    QLabel, QCheckBox, QListWidget, QFileDialog, QStyle, QStackedLayout, QMessageBox
)
from PySide6.QtCore import Qt
from NewLogicGroup import searchPLCInfoNVD

search_terms = []

def toggle_detailed_search(state):
    global detailed_search
    detailed_search = state == Qt.Checked

def empty_method():
    pass

def show_error_popup(message):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle("Error")
    msg_box.exec()

def handle_search(source, results_list, device_name_edit=None):
    global search_terms
    if source == "Individual":
        device_name = device_name_edit.text().strip() if device_name_edit else ""
        if not device_name:
            show_error_popup("Please fill in the device name.")
            return
        
        search_terms.append((device_name, 1))
    
    try:
        deviceInfoList = searchPLCInfoNVD(search_terms)  # Pass the list of search terms with counts
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

def create_bottom_layout():
    bottom_layout = QHBoxLayout()
    imported_devices_label = QLabel("Imported Devices")
    bottom_layout.addWidget(imported_devices_label, alignment=Qt.AlignLeft)

    detailed_search_layout = QHBoxLayout()
    detailed_search_label = QLabel("Detailed Search")
    detailed_search_checkbox = QCheckBox()
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

def create_group_layout():
    group_layout = QVBoxLayout()

    group_file_layout = QHBoxLayout()
    import_file_button = QPushButton()
    import_file_button.setIcon(app.style().standardIcon(QStyle.SP_DirOpenIcon))
    import_file_button.setFixedSize(20, 20)  # Adjusted size
    group_textbox = QLineEdit()
    group_textbox.setReadOnly(True)
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

def print_search_terms():
    print(search_terms)

def main():
    global app
    app = QApplication([])

    # Main Window
    window = QWidget()
    main_layout = QVBoxLayout()

    # Dropdown for Individual and Group
    dropdown = QComboBox()
    dropdown.addItems(["Individual", "Group"])
    main_layout.addWidget(dropdown)

    # Stacked Layout for Individual and Group views
    stacked_layout = QStackedLayout()

    individual_widget = QWidget()
    individual_widget.setLayout(create_individual_layout())
    stacked_layout.addWidget(individual_widget)

    group_widget = QWidget()
    group_widget.setLayout(create_group_layout())
    stacked_layout.addWidget(group_widget)

    def switch_view(index):
        stacked_layout.setCurrentIndex(index)

    dropdown.currentIndexChanged.connect(switch_view)
    main_layout.addLayout(stacked_layout)

    # Temp button to print search_terms
    temp_button = QPushButton("Print Search Terms")
    temp_button.clicked.connect(print_search_terms)
    main_layout.addWidget(temp_button)

    window.setLayout(main_layout)
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
