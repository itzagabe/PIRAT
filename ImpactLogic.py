import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QButtonGroup, QToolButton, QFrame
from PySide6.QtCore import Qt

def create_button_group(severity_list):
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
        if i == len(severity_list) - 1:
            button.setStyleSheet(button.styleSheet() + "QPushButton { border-top-right-radius: 3px; border-bottom-right-radius: 3px; }")
        button_group.addButton(button)
        button_layout.addWidget(button)

        if label == "None":
            button.setChecked(True)

    return button_group, button_layout

def create_category_layout(main_layout, button_groups_1, button_groups_2, active_items, category_list):
    severity_list = [
        ("None", 0, "#A9A9A9"),
        ("Low", 1, "lightgreen"),
        ("Medium", 2, "orange"),
        ("High", 3, "lightcoral")
    ]

    for category_name, subcategories in category_list:
        active_items.append(category_name)  # By default, main categories are active
        category_layout = QHBoxLayout()

        # Frame for dropdown button and category/subcategory labels
        frame_labels = QFrame()
        layout_labels = QVBoxLayout()
        layout_labels.setSpacing(0)
        layout_labels.setContentsMargins(0, 4, 0, 0)
        frame_labels.setLayout(layout_labels)

        # Frame for severity ratings group 1
        frame_group1 = QFrame()
        layout_group1 = QVBoxLayout()
        layout_group1.setSpacing(0)
        layout_group1.setContentsMargins(0, 4, 0, 0)
        frame_group1.setLayout(layout_group1)

        # Frame for severity ratings group 2
        frame_group2 = QFrame()
        layout_group2 = QVBoxLayout()
        layout_group2.setSpacing(0)
        layout_group2.setContentsMargins(0, 4, 0, 0)
        frame_group2.setLayout(layout_group2)

        if subcategories:
            toggle_button = QToolButton()
            toggle_button.setText('▶')
            toggle_button.setCheckable(True)
            toggle_button.setChecked(False)
            toggle_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            toggle_button.setArrowType(Qt.RightArrow)
            toggle_button.toggled.connect(lambda checked, btn=toggle_button, cat=category_name, subs=subcategories: toggle_subcategories(checked, btn, cat, subs, active_items, category_list, button_groups_1))
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

        button_group_1, button_layout_1 = create_button_group(severity_list)
        button_group_2, button_layout_2 = create_button_group(severity_list)

        layout_group1.addLayout(button_layout_1)
        layout_group2.addLayout(button_layout_2)

        category_layout.addWidget(frame_labels)
        category_layout.addWidget(frame_group1)
        category_layout.addWidget(frame_group2)

        main_layout.addLayout(category_layout)
        button_groups_1[category_name.strip()] = button_group_1
        button_groups_2[category_name.strip()] = button_group_2

        if subcategories:
            subcategory_frame = QFrame()
            subcategory_frame.setFrameShape(QFrame.NoFrame)
            subcategory_layout = QVBoxLayout()
            subcategory_layout.setSpacing(0)
            subcategory_layout.setContentsMargins(20, 0, 0, 0)

            for subcategory in subcategories:
                subcategory_layout.addLayout(create_subcategory_layout(subcategory, severity_list, button_groups_1, button_groups_2, category_name.strip()))

            subcategory_frame.setLayout(subcategory_layout)
            subcategory_frame.setVisible(False)
            main_layout.addWidget(subcategory_frame)
            toggle_button.toggled.connect(lambda checked, frame=subcategory_frame: frame.setVisible(checked))

def create_subcategory_layout(subcategory, severity_list, button_groups_1, button_groups_2, parent_category):
    subcategory_layout = QHBoxLayout()

    # Frame for dropdown button and subcategory labels
    frame_labels = QFrame()
    layout_labels = QVBoxLayout()
    layout_labels.setSpacing(0)
    layout_labels.setContentsMargins(20, 0, 0, 0)
    frame_labels.setLayout(layout_labels)

    # Frame for severity ratings group 1
    frame_group1 = QFrame()
    layout_group1 = QVBoxLayout()
    layout_group1.setSpacing(0)
    layout_group1.setContentsMargins(0, 0, 0, 1)
    frame_group1.setLayout(layout_group1)

    # Frame for severity ratings group 2
    frame_group2 = QFrame()
    layout_group2 = QVBoxLayout()
    layout_group2.setSpacing(0)
    layout_group2.setContentsMargins(6, 0, 0, 2)
    frame_group2.setLayout(layout_group2)

    subcategory_label = QLabel(subcategory)
    subcategory_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    layout_labels.addWidget(subcategory_label)

    button_group_1, subcategory_button_layout_1 = create_button_group(severity_list)
    button_group_2, subcategory_button_layout_2 = create_button_group(severity_list)

    layout_group1.addLayout(subcategory_button_layout_1)
    layout_group2.addLayout(subcategory_button_layout_2)

    subcategory_layout.addWidget(frame_labels)
    subcategory_layout.addWidget(frame_group1)
    subcategory_layout.addWidget(frame_group2)

    button_groups_1[f"{parent_category} - {subcategory}"] = button_group_1
    button_groups_2[f"{parent_category} - {subcategory}"] = button_group_2

    return subcategory_layout

def toggle_subcategories(checked, button, category_name, subcategories, active_items, category_list, button_groups_1):
    if checked:
        if category_name in active_items:
            active_items.remove(category_name)
        active_items.extend(f"{category_name} - {sub}" for sub in subcategories if f"{category_name} - {sub}" not in active_items)
        # Disable main category buttons
        for button in button_groups_1[category_name.strip()].buttons():
            button.setDisabled(True)
    else:
        active_items.append(category_name)
        for sub in subcategories:
            sub_item = f"{category_name} - {sub}"
            if sub_item in active_items:
                active_items.remove(sub_item)
        # Enable main category buttons
        for button in button_groups_1[category_name.strip()].buttons():
            button.setDisabled(False)
    reorder_active_items(active_items, category_list)

def reorder_active_items(active_items, category_list):
    ordered_active_items = []
    for category_name, subcategories in category_list:
        if category_name in active_items:
            ordered_active_items.append(category_name)
        for subcategory in subcategories:
            sub_item = f"{category_name} - {subcategory}"
            if sub_item in active_items:
                ordered_active_items.append(sub_item)
    active_items[:] = ordered_active_items

def display_results(button_groups_1, button_groups_2, active_items):
    print("Group 1:")
    for item in active_items:
        if item in button_groups_1:
            button_group = button_groups_1[item]
            selected_button = button_group.checkedButton()
            if selected_button:
                severity_label = selected_button.text()
                severity_value = selected_button.property('severity_value')
                print(f"{item}: {severity_label} ({severity_value})")
    print("Group 2:")
    for item in active_items:
        if item in button_groups_2:
            button_group = button_groups_2[item]
            selected_button = button_group.checkedButton()
            if selected_button:
                severity_label = selected_button.text()
                severity_value = selected_button.property('severity_value')
                print(f"{item}: {severity_label} ({severity_value})")
    print('')

def initialize_layout(main_layout):
    button_groups_1 = {}
    button_groups_2 = {}
    active_items = []

    category_list = [
        ("Operational", ["Proprietary", "System"]),
        ("Safety", []),
        ("Financial", []),
        ("Privacy and Legislative", ["Societal Loss", 'Regulatory Loss', 'Environmental Loss'])
    ]

    create_category_layout(main_layout, button_groups_1, button_groups_2, active_items, category_list)

    return (button_groups_1, button_groups_2), active_items
