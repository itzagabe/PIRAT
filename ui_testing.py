import tkinter as tk
from tkinter import ttk

def tab1_content():
    label = tk.Label(tab1, text="Content for Tab 1")
    label.pack(padx=10, pady=10)
    instruction_label = instructionLabelSettings()

def tab2_content():
    label = tk.Label(tab2, text="Content for Tab 2")
    label.pack(padx=10, pady=10)

def welcomeLabelSettings():
    headText = "Welcome to PIRAT - Python Risk Assessment Tool!\n"
    firstLine = "This tool allows you to estimate the risk of compromise of PLC devices by using the information\nfrom the National Vulnerability Database (NVD) and the MITRE ATT&CK Framework\n"
    nextLine = "How do we do it?\nWe process the information from the NVD and MITRE ATT&CK databases and feed it to our risk assessment formula to\n determine the risk factor of the PLC devices"
    
    welcome_label = tk.Label(header_frame, text=headText + firstLine + nextLine, font=("Arial", 14), bg="red")
    welcome_label.pack(pady=10, padx=10)
    
    return welcome_label

def instructionLabelSettings():
    instText = "How to use:\n"
    instText += "1. Please select a PLC manufacturer and the industry of your organization from the corresponding dropdown menus\n"
    instText += "2. Select the appropriate output type - 'Risk assessment only' is the default. If 'Verbose' selected, specify whether you want the CVE descriptions to be outputted\n"
    instText += "3. Enter the model of the PLC in the search bar - do not include the name of the manufacturer\n"
    instText += "4. Check the appropriate impact boxes based on the consequences as a result of a PLC attack\n"
    instructionLabel = tk.Label(tab1, text=instText, font=("Arial", 18))
    instructionLabel.place(relx = 0.12, rely = 0.05)
    return instructionLabel


# Create the main window
root = tk.Tk()
root.title("Tabbed Window")

# Create a frame above the notebook
header_frame = ttk.Frame(root)
header_frame.pack(side="top", fill="x")

# Add a label to the header frame
header_label = tk.Label(header_frame, text="Test", font=("Helvetica", 14))
header_label.pack(pady=10)

# Call the function to create and center the welcome label
welcome_label = welcomeLabelSettings()

# Create a notebook (tabbed interface)
notebook = ttk.Notebook(root)

# Create tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

notebook.add(tab1, text="Tab 1")
notebook.add(tab2, text="Tab 2")

# Add content to the tabs
tab1_content()
tab2_content()

# Pack the notebook to make it visible
notebook.pack(expand=True, fill="both")

# Start the Tkinter event loop
root.mainloop()
