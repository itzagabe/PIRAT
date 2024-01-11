import tkinter as tk
from tkinter import ttk

def file_import():
    # Implementation for the import button
    print("Import button clicked")

def file_save():
    # Implementation for the save button
    print("Save button clicked")

def help_popup():
    # Implementation for the help button popup
    popup = tk.Toplevel(root)
    popup.title("Under construction")
    label = tk.Label(popup, text="Under construction")
    label.pack(padx=10, pady=10)

def create_menu_bar():
    menu_bar = tk.Menu(root)

    # File Dropdown
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Import", command=file_import)
    file_menu.add_command(label="Save", command=file_save)
    menu_bar.add_cascade(label="File", menu=file_menu)

    # Help Button
    menu_bar.add_command(label="Help", command=help_popup)

    root.config(menu=menu_bar)

def create_frame():
    frame = tk.Frame(root, width=400, height=180, bd=1, relief=tk.SUNKEN)
    frame.pack(side=tk.TOP, fill=tk.X)

    # Bold and center "Welcome to PIRAT - Python Risk Assessment Tool!"
    title_label = tk.Label(frame, text="Welcome to PIRAT - Python Risk Assessment Tool!", font=('TkDefaultFont', 12, 'bold'), anchor='center')
    title_label.pack(pady=5)

    # Left-aligned text
    text1_label = tk.Label(frame, text="This tool allows you to estimate the risk of compromise of PLC devices by using the information from the National Vulnerability Database (NVD) and the MITRE ATT&CK Framework.", justify=tk.LEFT)
    text1_label.pack(padx=10, pady=5, anchor='w')

    # Bold and center "How do we do it?"
    bold_center_label = tk.Label(frame, text="How do we do it?", font=('TkDefaultFont', 10, 'bold'), anchor='center')
    bold_center_label.pack(pady=5)

    # Left-aligned text
    text2_label = tk.Label(frame, text="We process the information from the NVD and MITRE ATT&CK databases and feed it to our risk assessment formula to determine the risk factor of the PLC devices.", justify=tk.LEFT)
    text2_label.pack(padx=10, pady=5, anchor='w')

    return frame

def onEntryClick(event):
    event.widget.delete(0, tk.END)

def entryBox(frame):
    global entryField
    entryVar = tk.StringVar()
    entryVar.set("Enter the PLC model to analyze:")
    entryField = tk.Entry(frame, width=50, textvariable=entryVar)
    entryField.bind("<Button-1>", onEntryClick)
    return entryField


def industryDropdownSettings(frame):
    global industryVariable
    OPTIONS = ["Aerospace","Chemical","Cyber","IT","Health","Law","Manufacturing","Maritime","Military",
               "Gambling", "Education","Finance","Government","Defense","Energy", "Engineering",
               "Petroleum","Retail","Technology","Telecom","Transportation"]
    OPTIONS = sorted(OPTIONS)

    industryVariable = tk.StringVar(root)
    industryVariable.set("Select industry:") # default value
    industryDropdown = tk.OptionMenu(frame, industryVariable, *OPTIONS)
    industryDropdown.config(width=20)
    return industryDropdown

def manufacturerDropdownSettings(frame):
    global manufacturerVariable
    OPTIONS = ["ABB","Allen Bradley","Beckhoff","Delta","Eaton","Fatek","Festo",
               "Fuji","GeFanuc","Hitachi","Honeywell","Inovance","Kinco","LG",
               "Mitsubishi","Omron","Panasonic","Schneider Electric","Siemens",
               "Toshiba","Unitronics","Wago","Yokogawa","Other"]

    manufacturerVariable = tk.StringVar(root)
    manufacturerVariable.set("Select PLC Manufacturer:") # default value

    manufacturerDropdown = tk.OptionMenu(frame, manufacturerVariable, *OPTIONS)
    manufacturerDropdown.config(width=20)
    #manufacturerDropdown.place(relx = 0.20, rely = 0.52, width = 230)
    return manufacturerDropdown

def radioButtonSettings(frame):
    global typeVariable

    R1 = tk.Radiobutton(frame, text="Risk assessment only", variable=typeVariable, value=1)
    R1.place(relx = 0.34, rely = 0.495)
    typeVariable.set(1) # Set to 1 by default

    # Verbose will output CVE description + any relevant MITRE ATT&CK info
    R2 = tk.Radiobutton(frame, text="Verbose", variable=typeVariable, value=2)
    R2.place(relx = 0.34, rely = 0.52)

    return R1, R2


def create_tab1(notebook):
    tab1 = ttk.Frame(notebook)

    textTop = """How to use:
    1. Please select a PLC manufacturer and the industry of your organization from the corresponding dropdown menus
    2. Select the appropriate output type - 'Risk assessment only' is the default. If 'Verbose' selected, specify whether you want the CVE descriptions to be outputted
    3. Enter the model of the PLC in the search bar - do not include the name of the manufacturer
    4. Check the appropriate impact boxes based on the consequences as a result of a PLC attack"""
    tab1_label = tk.Label(tab1, text=textTop, justify=tk.LEFT)
    tab1_label.pack()
    

    # Create frames for left and right sides with borders
    left_frame = tk.Frame(tab1, bd=1, relief=tk.SUNKEN)
    
    entryBox(left_frame).pack(pady = 10) #gets entry field

    left_left_frame = tk.Frame(left_frame, bd=1, relief=tk.SUNKEN)
    left_right_frame = tk.Frame(left_frame, bd=1, relief=tk.SUNKEN)

    # Left side UI elements
    industryDropdownSettings(left_left_frame).grid(row=1, column=0, padx=10, pady=5, sticky='w') # Industry Dropdown
    manufacturerDropdownSettings(left_left_frame).grid(row=2, column=0, padx=10, pady=5, sticky='w') #Manufacturer Dropdown

    typeText = "Select type of output:"
    typeLabel = tk.Label(left_left_frame, text=typeText, justify=tk.LEFT)
    typeLabel.grid(row=0, column=1, padx=10, pady=5, sticky='w')

    #radioButtonSettings(left_left_frame)

    left_left_frame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

    # Updated: Specify the column for left_right_frame
    left_right_label = tk.Label(left_right_frame, text="Left Right Side")
    left_right_button = tk.Button(left_right_frame, text="Left Right Button")

    left_right_label.grid(row=0, column=1, padx=10, pady=5, sticky='w')  # Updated: Set column to 1
    left_right_button.grid(row=1, column=1, padx=10, pady=5, sticky='w')  # Updated: Set column to 1
    left_right_frame.pack(side=tk.RIGHT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

    left_frame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

    # Right side UI elements
    right_frame = tk.Frame(tab1, bd=1, relief=tk.SUNKEN)
    right_label = tk.Label(right_frame, text="Right Side")
    right_button = tk.Button(right_frame, text="Right Button", command=lambda: print(f" MV: {manufacturerVariable.get()}, IV: {industryVariable.get()}"))
    right_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')
    right_button.grid(row=1, column=0, padx=10, pady=5, sticky='e')
    right_frame.pack(side=tk.RIGHT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

    notebook.add(tab1, text="Individual PLC Calculation")

def create_tab2(notebook):
    tab2 = ttk.Frame(notebook)
    tab2_label = tk.Label(tab2, text="Dummy 2")
    tab2_label.pack()
    notebook.add(tab2, text="Group PLC Calculation")

def create_notebook():
    notebook = ttk.Notebook(root)
    create_tab1(notebook)
    create_tab2(notebook)
    notebook.pack(expand=1, fill="both")

def main():
    create_menu_bar()
    create_frame()
    create_notebook()
    # Lock window resizing
    root.resizable(False, False)

    # Run the application
    root.mainloop()

# Create the main window
root = tk.Tk()
root.title("PRIAT - Risk Assessment Tool")
root.geometry("1280x720")
root.resizable(False, False)

if __name__ == "__main__":
    main()
