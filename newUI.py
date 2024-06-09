import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QSizePolicy, QToolButton, QLabel, QSpacerItem, QGridLayout
from PySide6.QtCore import Qt
from ImpactLogic import CreateLayout, DisplayResults, MapDataCategories

Low = "#90EE90"  # Low
Medium = "#ffd68b"  # Medium
High = "#f09d9d"  # High

def interpolate_color(start_color, end_color, factor):
    # Helper function to interpolate between two colors
    start_color = start_color.lstrip('#')
    end_color = end_color.lstrip('#')
    sr, sg, sb = int(start_color[0:2], 16), int(start_color[2:4], 16), int(start_color[4:6], 16)
    er, eg, eb = int(end_color[0:2], 16), int(end_color[2:4], 16), int(end_color[4:6], 16)
    
    r = int(sr + (er - sr) * factor)
    g = int(sg + (eg - sg) * factor)
    b = int(sb + (eb - sb) * factor)
    
    return f'#{r:02x}{g:02x}{b:02x}'

def set_tooltips(widget, tooltips):
    # Recursively find QLabel widgets and set their tooltips
    for child in widget.findChildren(QWidget):
        if isinstance(child, QLabel):
            label_text = child.text().strip()
            if label_text in tooltips:
                child.setToolTip(tooltips[label_text])
        set_tooltips(child, tooltips)

def create_generic_layout(severity_list, category_list, num_button_groups, update_func, default_color, tooltips):
    def update_button(button_groups, active_items, result_button):
        returnValue = DisplayResults(button_groups, active_items)[0]
        update_func(returnValue, result_button)

    # Create the main layout and the UI frame
    main_layout = QVBoxLayout()
    main_layout.setSpacing(10)
    main_layout.setContentsMargins(0, 0, 0, 0)
    
    ui_frame = QFrame()
    ui_layout = QVBoxLayout(ui_frame)
    ui_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    ui_layout.setSpacing(10)
    ui_layout.setContentsMargins(0, 0, 0, 0)
    ui_frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    button_groups, active_items = CreateLayout(ui_layout, severity_list, category_list, num_button_groups)

    # Set tooltips for the category labels
    set_tooltips(ui_frame, tooltips)

    # Create the result button
    result_button = QPushButton("")
    result_button.setEnabled(False)
    result_button.setStyleSheet(f"border-radius: 3px; color: black; background-color: {default_color};")
    result_button.setFixedHeight(20)
    result_button.setFixedWidth(230)
    result_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    result_button.setToolTip("This button shows the calculated severity value.")

    # Update the result button initially
    update_button(button_groups, active_items, result_button)

    # Connect the button groups to update the result button instantly
    for button_group_dict in button_groups:
        for button_group in button_group_dict.values():
            button_group.buttonToggled.connect(lambda: update_button(button_groups, active_items, result_button))

    # Add toggle connections for subcategory dropdowns
    subcategory_buttons = ui_frame.findChildren(QToolButton)
    for btn in subcategory_buttons:
        btn.toggled.connect(lambda: update_button(button_groups, active_items, result_button))

    # Add the result button directly to the UI frame layout
    ui_layout.addWidget(result_button, alignment=Qt.AlignTop | Qt.AlignHCenter)

    return ui_frame

def update_impact_layout(returnValue, result_button):
    returnValue2 = sum(val[3] for val in returnValue) / len(returnValue) if returnValue else 0
    colors = [
        (0, "#bababa"),  # None
        (0.3, Low),  # Low
        (0.6, Medium),  # Medium
        (1, High)  # High
    ]
    
    for i in range(len(colors) - 1):
        if colors[i][0] <= returnValue2 <= colors[i + 1][0]:
            factor = (returnValue2 - colors[i][0]) / (colors[i + 1][0] - colors[i][0])
            color = interpolate_color(colors[i][1], colors[i + 1][1], factor)
            break
    else:
        color = colors[-1][1]

    result_button.setText(f"Average Severity: {returnValue2:.2f}")
    result_button.setStyleSheet(f"background-color: {color}; border-radius: 3px; color: black;")

def update_data_layout(returnValue, result_button):
    chart_result = MapDataCategories(returnValue)
    severity_label, severity_value = chart_result
    color_map = {
        "Very Low": "#d4f1d4",
        "Low": Low,
        "Moderate": Medium,
        "High": High,
        "Very High": "#f28888"
    }
    color = color_map.get(severity_label, "#FFFFFF")
    result_button.setText(f"{severity_label} ({severity_value})")
    result_button.setStyleSheet(f"background-color: {color}; border-radius: 3px; color: black;")

def ImpactCategories():
    severity_list = [
        ("None", 0, "#bababa"),
        ("Low", 0.3, Low),
        ("Medium", 0.6, Medium),
        ("High", 1, High)
    ]
    category_list = [
        ("Operational", ["Proprietary", "System"]),
        ("Safety", []),
        ("Financial", []),
        ("Privacy and Legislative", ["Societal Loss", 'Regulatory Loss', 'Environmental Loss'])
    ]
    num_button_groups = 2
    default_color = "#bababa"
    tooltips = {
        "Operational": "Operational impact category",
        "Proprietary": "Operational - Proprietary subcategory",
        "System": "Operational - System subcategory",
        "Safety": "Safety impact category",
        "Financial": "Financial impact category",
        "Privacy and Legislative": "Privacy and Legislative impact category",
        "Societal Loss": "Privacy and Legislative - Societal Loss subcategory",
        "Regulatory Loss": "Privacy and Legislative - Regulatory Loss subcategory",
        "Environmental Loss": "Privacy and Legislative - Environmental Loss subcategory"
    }

    return create_generic_layout(severity_list, category_list, num_button_groups, update_impact_layout, default_color, tooltips)

def DataCategories():
    severity_list = [
        ("Low", 1, Low),
        ("Medium", 2, Medium),
        ("High", 3, High),
    ]
    category_list = ['Data Rate', 'Publishers']
    num_button_groups = 1
    default_color = "#90EE90"
    tooltips = {
        "Data Rate": "Impact based on data rate",
        "Publishers": "Impact based on number of publishers"
    }

    return create_generic_layout(severity_list, category_list, num_button_groups, update_data_layout, default_color, tooltips)

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Main UI")

    # Setup the impact and data logic frames
    impact_frame = ImpactCategories()
    data_frame = DataCategories()
    
    # Create a main grid layout and add both frames to it at specific locations
    main_layout = QGridLayout()
    main_layout.setSpacing(10)
    main_layout.setContentsMargins(0, 0, 0, 0)
    
    # Add the data and impact frames to specific positions
    main_layout.addWidget(data_frame, 0, 0, Qt.AlignTop | Qt.AlignLeft)
    main_layout.addWidget(impact_frame, 0, 1, Qt.AlignTop | Qt.AlignLeft)
    
    # Create a container widget and set its layout
    container = QWidget()
    container.setLayout(main_layout)
    window.setCentralWidget(container)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
