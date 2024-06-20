import threading
from nvd import *
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QListWidget, QPushButton, QLabel
from PySide6.QtCore import Qt
import datetime

officialCPE = []
notFoundDevices = []
refineSearchDevices = []
timeoutTimer = 5

def searchPLCInfoNVD(searchTermList, refinedSearch = True):
    global officialCPE, notFoundDevices, refineSearchDevices, timeoutTimer
    # Clear global lists
    officialCPE = []
    notFoundDevices = []
    refineSearchDevices = []

    listLength = len(searchTermList)
    for idx, (cpeTerm, count) in enumerate(searchTermList):
        if len(cpeTerm) == 1:
            refineSearchDevices.append(cpeTerm)
            continue
        cpeList = []
        event = threading.Event()
        threading.Thread(target=call_searchNVDCPE, args=(cpeTerm, cpeList, event)).start()

        if not event.wait(timeoutTimer):  # 20 seconds timeout
            refineSearchDevices.append(cpeTerm)
            continue
        
        if not refinedSearch:
            cpeList = [cpe for cpe in cpeList if "firmware" not in cpe.cpeName] # remove firmware from search

        if len(cpeList) == 0:
            notFoundDevices.append(cpeTerm)
        elif len(cpeList) == 1 or not refinedSearch:
            officialCPE.append((cpeList[0].cpeName, count))
        else:
            selected_cpe = chooseWhichCPE(cpeList, cpeTerm, idx, listLength, count)
            if selected_cpe:
                officialCPE.append((selected_cpe, count))
            else:
                notFoundDevices.append(cpeTerm)

    if notFoundDevices or refineSearchDevices:
        showNotFoundDevicesPopup(notFoundDevices, refineSearchDevices)

    # Create the final list with CPEs and their corresponding CVEs
    cpe_cve_list = []
    for cpe, count in officialCPE:
        cve_list = searchNVD(cpe)
        refinedCVEList = getLatestCVEList(cve_list) # get refined CVE list
        cpe_cve_list.extend([(cpe, [(cve, True) for cve in refinedCVEList])] * count)

    return cpe_cve_list

def call_searchNVDCPE(cpeTerm, cpeList, event):
    try:
        result = searchNVDCPE(cpeTerm)
        if result:
            cpeList.extend(result)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        event.set()

def chooseWhichCPE(cpeList, cpeTerm, idx, listLength, count):
    app = QApplication.instance() or QApplication([])

    dialog = QDialog()
    dialog.setWindowTitle(f"Choose CPE for \"{cpeTerm}\" ({idx + 1} / {listLength}) - {count} devices")
    dialog.setMinimumWidth(1500)

    layout = QVBoxLayout()
    dialog.setLayout(layout)

    list_widget = QListWidget()
    cpeNames = [cpe.cpeName for cpe in cpeList]  # Extract cpeName from each element in cpeList
    list_widget.addItems(cpeNames)
    layout.addWidget(list_widget)

    confirm_button = QPushButton("Select")
    confirm_button.setStyleSheet("background-color: blue; border-radius: 3px; color: white;")
    layout.addWidget(confirm_button)

    def on_confirm():
        dialog.accept()

    confirm_button.clicked.connect(on_confirm)

    if dialog.exec():
        selected_item = list_widget.currentItem()
        return selected_item.text() if selected_item else None
    return None

def showNotFoundDevicesPopup(notFoundDevices, refineSearchDevices):
    app = QApplication.instance() or QApplication([])

    dialog = QDialog()
    dialog.setWindowTitle("Devices Not Found or Need Refinement")
    dialog.setMinimumWidth(1500)  # Make the pop-out window wider

    layout = QVBoxLayout()
    dialog.setLayout(layout)

    if notFoundDevices:
        label_not_found = QLabel("The following devices could not be found:")
        layout.addWidget(label_not_found)
        list_widget_not_found = QListWidget()
        list_widget_not_found.addItems(notFoundDevices)
        layout.addWidget(list_widget_not_found)

    if refineSearchDevices:
        label_refine_search = QLabel("The following devices need search refinement:")
        layout.addWidget(label_refine_search)
        list_widget_refine_search = QListWidget()
        list_widget_refine_search.addItems(refineSearchDevices)
        layout.addWidget(list_widget_refine_search)

    close_button = QPushButton("Close")
    close_button.setStyleSheet("background-color: blue; border-radius: 3px; color: white;")
    layout.addWidget(close_button)

    close_button.clicked.connect(dialog.accept)

    dialog.exec()


# def searchNVD(cpe):
#     # Mock implementation of searchNVD function. Replace with actual implementation.
#     # This should return a list of CVEs for the given CPE.
#     class MockCVE:
#         def __init__(self, id):
#             self.id = id

#     return [MockCVE("CVE-2021-1234"), MockCVE("CVE-2021-5678")]  # Example CVEs

if __name__ == "__main__":
    searchPLCInfoNVD([("simatic", 2), ("siemens", 1)])
    print("Official CPE List:", officialCPE)
