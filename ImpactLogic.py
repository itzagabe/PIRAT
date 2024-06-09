import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QButtonGroup, QToolButton, QFrame
from PySide6.QtCore import Qt

def ButtonGroup(severity_list):
    button_group = QButtonGroup()
    button_layout = QHBoxLayout()
    button_layout.setSpacing(0)  # No spaces between severity buttons

    for i, (label, value, color) in enumerate(severity_list):
        button = QPushButton(label)
        button.setFixedSize(60, 30)
        button.setCheckable(True)
        button.setProperty('severity_value', value)
        button.setProperty('severity_color', color)
        button.setStyleSheet(f"QPushButton {{ border-radius: 0px; background-color: lightgray; }} QPushButton:checked {{ background-color: {color}; }} QPushButton:checked:disabled {{ background-color: gray; }} QPushButton:disabled:!checked {{ background-color: darkgray; }}")
        if i == 0:
            button.setStyleSheet(button.styleSheet() + "QPushButton { border-top-left-radius: 3px; border-bottom-left-radius: 3px; }")
            button.setChecked(True)
        if i == len(severity_list) - 1:
            button.setStyleSheet(button.styleSheet() + "QPushButton { border-top-right-radius: 3px; border-bottom-right-radius: 3px; }")
        button_group.addButton(button)
        button_layout.addWidget(button)
           
    return button_group, button_layout

def CatLayout(main_layout, button_groups_list, category_list, severity_list):
    if isinstance(category_list, str):
        category_list = [(category_list, [])]
    elif isinstance(category_list, list):
        category_list = [(item, []) if isinstance(item, str) else item for item in category_list]
    active_items = None
    if any(subcategories for _, subcategories in category_list):
        active_items = []

    for category_name, subcategories in category_list:
        if active_items is not None:
            active_items.append(category_name)  # By default, main categories are active
        category_layout = QHBoxLayout()

        # Frame for dropdown button and category/subcategory labels
        frame_labels = QFrame()
        layout_labels = QVBoxLayout()
        layout_labels.setSpacing(0)
        layout_labels.setContentsMargins(0, 4, 0, 0)
        frame_labels.setLayout(layout_labels)

        frames = []
        layouts = []

        for _ in button_groups_list:
            frame = QFrame()
            layout = QVBoxLayout()
            layout.setSpacing(0)
            layout.setContentsMargins(0, 4, 0, 0)
            frame.setLayout(layout)
            frames.append(frame)
            layouts.append(layout)

        if subcategories:
            toggle_button = QToolButton()
            toggle_button.setText('▶')
            toggle_button.setCheckable(True)
            toggle_button.setChecked(False)
            toggle_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            toggle_button.setArrowType(Qt.RightArrow)
            toggle_button.toggled.connect(lambda checked, btn=toggle_button, cat=category_name, subs=subcategories: ToggleSubcat(checked, btn, cat, subs, active_items, category_list, button_groups_list))
            category_layout.addWidget(toggle_button)
        else:
            dropdown_spacer = QWidget()
            dropdown_spacer.setFixedWidth(20)  # Dropdown button width for alignment
            category_layout.addWidget(dropdown_spacer)

        if not subcategories:
            category_name = " " + category_name  # Add a leading space for categories without subcategories
        category_label = QLabel(category_name)
        category_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout_labels.addWidget(category_label)  # Line determining location of the label

        for layout, button_groups in zip(layouts, button_groups_list):
            button_group, button_layout = ButtonGroup(severity_list)
            layout.addLayout(button_layout)
            button_groups[category_name.strip()] = button_group

        category_layout.addWidget(frame_labels)
        for frame in frames:
            category_layout.addWidget(frame)

        main_layout.addLayout(category_layout)

        if subcategories:
            subcategory_frame = QFrame()
            subcategory_frame.setFrameShape(QFrame.NoFrame)
            subcategory_layout = QVBoxLayout()
            subcategory_layout.setSpacing(0)
            subcategory_layout.setContentsMargins(20, 0, 0, 0)

            for subcategory in subcategories:
                subcategory_layout.addLayout(SubcatLayout(subcategory, severity_list, button_groups_list, category_name.strip()))

            subcategory_frame.setLayout(subcategory_layout)
            subcategory_frame.setVisible(False)
            main_layout.addWidget(subcategory_frame)
            toggle_button.toggled.connect(lambda checked, frame=subcategory_frame: frame.setVisible(checked))

    return active_items

def SubcatLayout(subcategory, severity_list, button_groups_list, parent_category):
    subcategory_layout = QHBoxLayout()

    # Frame for dropdown button and subcategory labels
    frame_labels = QFrame()
    layout_labels = QVBoxLayout()
    layout_labels.setSpacing(0)
    layout_labels.setContentsMargins(20, 0, 0, 0)
    frame_labels.setLayout(layout_labels)

    frames = []
    layouts = []

    for _ in button_groups_list:
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 0, 0, 1)
        frame.setLayout(layout)
        frames.append(frame)
        layouts.append(layout)

    subcategory_label = QLabel(subcategory)
    subcategory_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    layout_labels.addWidget(subcategory_label)

    for layout, button_groups in zip(layouts, button_groups_list):
        button_group, subcategory_button_layout = ButtonGroup(severity_list)
        layout.addLayout(subcategory_button_layout)
        button_groups[f"{parent_category} - {subcategory}"] = button_group

    subcategory_layout.addWidget(frame_labels)
    for frame in frames:
        subcategory_layout.addWidget(frame)

    return subcategory_layout

def ToggleSubcat(checked, button, category_name, subcategories, active_items, category_list, button_groups_list):
    if checked:
        if category_name in active_items:
            active_items.remove(category_name)
        active_items.extend(f"{category_name} - {sub}" for sub in subcategories if f"{category_name} - {sub}" not in active_items)
        # Disable main category buttons
        for button_groups in button_groups_list:
            for button in button_groups[category_name.strip()].buttons():
                button.setDisabled(True)
    else:
        active_items.append(category_name)
        for sub in subcategories:
            sub_item = f"{category_name} - {sub}"
            if sub_item in active_items:
                active_items.remove(sub_item)
        # Enable main category buttons
        for button_groups in button_groups_list:
            for button in button_groups[category_name.strip()].buttons():
                button.setDisabled(False)
    ReorderActiveItems(active_items, category_list)

def ReorderActiveItems(active_items, category_list):
    ordered_active_items = []
    for category_name, subcategories in category_list:
        if category_name in active_items:
            ordered_active_items.append(category_name)
        for subcategory in subcategories:
            sub_item = f"{category_name} - {subcategory}"
            if sub_item in active_items:
                ordered_active_items.append(sub_item)
    active_items[:] = ordered_active_items

def DisplayResults(button_groups_list, active_items):
    returnValue = []
    total_severity_value = 0
    num_categories = 0
    
    for idx, button_groups in enumerate(button_groups_list):
        for item in active_items or button_groups.keys():
            if item in button_groups:
                button_group = button_groups[item]
                selected_button = button_group.checkedButton()
                if selected_button:
                    severity_label = selected_button.text()
                    severity_value = selected_button.property('severity_value')
                    returnValue.append([idx + 1, item, severity_label, severity_value])  # Added group index (1-based)
                    total_severity_value += severity_value
                    num_categories += 1
    
    returnValue2 = total_severity_value / num_categories if num_categories > 0 else 0
    return returnValue, returnValue2

def CreateLayout(main_layout, severity_list, category_list, num_button_groups):
    button_groups_list = [{} for _ in range(num_button_groups)]  # Create a list of empty dictionaries for button groups
    active_items = CatLayout(main_layout, button_groups_list, category_list, severity_list)
    return button_groups_list, active_items

def MapDataCategories(returnValue):
    # Define the mapping from severity levels to indices
    severity_map = {"Low": 0, "Medium": 1, "High": 2}
    
    # Initialize variables to hold the severity levels for Data Rate and Publishers
    data_rate_level = None
    publishers_level = None

    # Extract the severity levels from returnValue
    for entry in returnValue:
        group, category, severity, value = entry
        if category == "Data Rate":
            data_rate_level = severity
        elif category == "Publishers":
            publishers_level = severity
    
    # Ensure both Data Rate and Publishers have been provided
    if data_rate_level is None or publishers_level is None:
        return "Incomplete data"

    # Convert severity levels to indices
    data_rate_index = severity_map.get(data_rate_level)
    publishers_index = severity_map.get(publishers_level)

    # Define the chart matrix with severity label and numerical value separately
    chart = [
        [["Very Low", 0.1], ["Low", 0.3], ["Moderate", 0.75]],
        [["Low", 0.3], ["Moderate", 0.75], ["High", 0.9]],
        [["Moderate", 0.75], ["High", 0.9], ["Very High", 1.0]]
    ]

    # Map the severity levels to the chart
    result = chart[publishers_index][data_rate_index]
    
    return result
