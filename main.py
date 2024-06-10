import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from ImportDevices import *
from newUI import *

def create_top_container():
    top_container = QFrame()
    top_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    top_layout = QVBoxLayout(top_container)
    top_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    top_layout.setSpacing(10)
    top_layout.setContentsMargins(0, 0, 0, 0)

    inner_container = create_inner_container()
    top_layout.addWidget(inner_container)

    horizontal_line = QFrame()
    horizontal_line.setFrameShape(QFrame.HLine)
    horizontal_line.setStyleSheet("background-color: grey;")
    horizontal_line.setFixedHeight(2)
    top_layout.addWidget(horizontal_line)

    return top_container

def create_inner_container():
    inner_container = QFrame()
    inner_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    inner_layout = QHBoxLayout(inner_container)
    inner_layout.setSpacing(10)
    inner_layout.setContentsMargins(0, 0, 0, 0)

    dropdown = QComboBox()
    dropdown.addItems(["Individual", "Group"])
    dropdown.setFixedSize(150, 30)
    dropdown.setStyleSheet("font-size: 14px; padding: 5px;")
    inner_layout.addWidget(dropdown)

    vertical_line = QFrame()
    vertical_line.setFrameShape(QFrame.VLine)
    vertical_line.setStyleSheet("background-color: grey;")
    vertical_line.setFixedHeight(30)
    inner_layout.addWidget(vertical_line)

    individual_widgets = create_individual_widgets(inner_layout)
    group_widgets = create_group_widgets(inner_layout)

    for widget in group_widgets:
        widget.hide()

    dropdown.currentIndexChanged.connect(
        lambda: dropdown_changed(dropdown, individual_widgets, group_widgets, individual_widgets[-1], group_widgets[-1])
    )

    return inner_container

def create_bottom_container():
    bottom_container = QWidget()
    bottom_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    bottom_layout = QHBoxLayout(bottom_container)
    bottom_layout.setSpacing(10)
    bottom_layout.setContentsMargins(0, 0, 0, 0)
    bottom_layout.setAlignment(Qt.AlignTop)

    impactFrame = ImpactCategories()
    impactFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    dataFrame = DataCategories()
    dataFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    policyFrame = PolicyCategories()
    policyFrame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    leftLayout = QVBoxLayout()
    leftLayout.setSpacing(10)
    leftLayout.setAlignment(Qt.AlignTop)
    leftLayout.addWidget(policyFrame)

    dataContainer = QFrame()
    dataContainerLayout = QVBoxLayout(dataContainer)
    dataContainerLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
    dataContainerLayout.addWidget(dataFrame)
    leftLayout.addWidget(dataContainer)

    bottom_layout.addLayout(leftLayout)
    bottom_layout.addWidget(impactFrame)

    bottom_container.setLayout(bottom_layout)
    return bottom_container

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Combined UI")

    main_container = QWidget()
    main_layout = QVBoxLayout(main_container)
    main_layout.setSpacing(10)
    main_layout.setContentsMargins(10, 10, 10, 10)

    top_container = create_top_container()
    main_layout.addWidget(top_container, alignment=Qt.AlignTop | Qt.AlignLeft)

    bottom_container = create_bottom_container()
    main_layout.addWidget(bottom_container, alignment=Qt.AlignTop | Qt.AlignLeft)

    print_button = QPushButton("Print Values")
    print_button.setFixedHeight(30)
    print_button.setFixedWidth(100)
    print_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    print_button.setToolTip("This button prints the values list.")
    print_button.clicked.connect(lambda: print("Values printed"))
    main_layout.addWidget(print_button, alignment=Qt.AlignTop | Qt.AlignLeft)

    window.setCentralWidget(main_container)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
