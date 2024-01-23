import tkinter as tk
from tkinter import ttk, filedialog
from logic2 import *
import threading

def ImportFile():
    # Open a file dialog for file selection
    filePath = filedialog.askopenfilename(title="Select a file", filetypes=[("All files", "*.*")])

    if filePath:
        # User selected a file, perform actions with the file_path
        print(f"Selected file: {filePath}")
    else:
        # User canceled file selection
        print("File selection canceled")

def FileSave():
    # Implementation for the save button
    messagebox.showinfo("File Saved", "File saved")
    print("Save button clicked")

def HelpPopup():
    # Implementation for the help button popup
    popup = tk.Toplevel(root)
    popup.title("Under construction")
    label = tk.Label(popup, text="Under construction")
    label.pack(padx=10, pady=10)

def CreateMenuBar():
    menuBar = tk.Menu(root)

    # File Dropdown
    fileMenu = tk.Menu(menuBar, tearoff=0)
    fileMenu.add_command(label="Import", command=ImportFile)
    fileMenu.add_command(label="Save", command=FileSave)
    menuBar.add_cascade(label="File", menu=fileMenu)

    # Help Button
    menuBar.add_command(label="Help", command=HelpPopup)

    root.config(menu=menuBar)

calculationRunning = False

def PerformCalc():
    global calculationRunning

    if CheckForError(entryField, manufacturerVariable.get(), checkboxList):
        calculationRunning = True
        risk = CalculateRisk(entryField.get(), industryVariable.get(), manufacturerVariable.get(), typeVariable.get(), cveDesc.get(), checkboxList)
        DisplayRisk(risk)


def DisplayRisk(riskVal):
    win = tk.Toplevel()
    win.wm_title("Risk evaluation")
    win.geometry("850x500")

    # Create text widget and specify size.
    outputBox = tk.Text(win)
    outputBox.place(relx = 0, rely = 0, width = 850, height = 500)
    # Scroll bar
    bar = tk.Scrollbar(outputBox)
    bar.pack(side = tk.RIGHT, fill = tk.Y)

    outputBox.config(font=('Courier New',18,'bold'), yscrollcommand = bar.set)
    
    # Insert output into textbox.
    outputBox.insert(tk.END, riskVal)

def CreateFrame():
    frame = tk.Frame(root, width=400, height=180, bd=1, relief=tk.SUNKEN)
    frame.pack(side=tk.TOP, fill=tk.X)

    # Welcome message
    bold1Label = tk.Label(frame, text="Welcome to PIRAT - Python Risk Assessment Tool!", font=('TkDefaultFont', 12, 'bold'), anchor='center')
    bold1Label.pack(pady=5)
    text1Label = tk.Label(frame, text="This tool allows you to estimate the risk of compromise of PLC devices by using the information from the National Vulnerability Database (NVD) and the MITRE ATT&CK Framework.", justify=tk.LEFT)
    text1Label.pack(padx=10, pady=5, anchor='w')
    bold2Label = tk.Label(frame, text="How do we do it?", font=('TkDefaultFont', 10, 'bold'), anchor='center')
    bold2Label.pack(pady=5)
    text2_label = tk.Label(frame, text="We process the information from the NVD and MITRE ATT&CK databases and feed it to our risk assessment formula to determine the risk factor of the PLC devices.", justify=tk.LEFT)
    text2_label.pack(padx=10, pady=5, anchor='w')

    return frame

def OnEntryClick(event):
    event.widget.delete(0, tk.END)

def EntryBox(frame):
    global entryField
    entryVar = tk.StringVar()
    entryVar.set("Enter the PLC model to analyze:")
    entryField = tk.Entry(frame, width=50, textvariable=entryVar)
    entryField.bind("<Button-1>", OnEntryClick)
    return entryField


def IndustryDropdownSettings(frame):
    global industryVariable
    #####################
    # Industry Variable #
    #####################
    OPTIONS = ["Aerospace","Chemical","Cyber","IT","Health","Law","Manufacturing","Maritime","Military",
               "Gambling", "Education","Finance","Government","Defense","Energy", "Engineering",
               "Petroleum","Retail","Technology","Telecom","Transportation"]
    OPTIONS = sorted(OPTIONS)

    industryVariable = tk.StringVar(root)
    industryVariable.set("Select industry:") # default value
    industryDropdown = tk.OptionMenu(frame, industryVariable, *OPTIONS)
    industryDropdown.config(width=20)
    industryDropdown.grid(row=1, column=0, padx=10, pady=5, sticky='w')

def ManufacturerDropdownSettings(frame):
    global manufacturerVariable
    #########################
    # Manufacturer Variable #
    #########################
    
    OPTIONS = ["ABB","Allen Bradley","Beckhoff","Delta","Eaton","Fatek","Festo",
               "Fuji","GeFanuc","Hitachi","Honeywell","Inovance","Kinco","LG",
               "Mitsubishi","Omron","Panasonic","Schneider Electric","Siemens",
               "Toshiba","Unitronics","Wago","Yokogawa","Other"]

    manufacturerVariable = tk.StringVar(root)
    manufacturerVariable.set("Select PLC Manufacturer:") # default value

    manufacturerDropdown = tk.OptionMenu(frame, manufacturerVariable, *OPTIONS)
    manufacturerDropdown.config(width=20)
    #manufacturerDropdown.place(relx = 0.20, rely = 0.52, width = 230)
    manufacturerDropdown.grid(row=2, column=0, padx=10, pady=5, sticky='w') #Manufacturer Dropdown

def RadioButtonSettings(frame):
    global typeVariable 
    #############################################
    # Either Risk assessment (1) or verbose (2) #
    #############################################
    typeVariable = tk.IntVar()

    typeText = "Select type of output:"
    typeLabel = tk.Label(frame, text=typeText, justify=tk.LEFT)
    typeLabel.grid(row=0, column=1, padx=10, pady=5, sticky='w')

    R1 = tk.Radiobutton(frame, text="Risk assessment only", variable=typeVariable, value=1, command=StateVerbose)
    typeVariable.set(1) # Set to 1 by default

    # Verbose will output CVE description + any relevant MITRE ATT&CK info
    R2 = tk.Radiobutton(frame, text="Verbose", variable=typeVariable, value=2, command=StateVerbose)

    R1.grid(row=1, column=1, padx=10, pady=5, sticky='w')
    R2.grid(row=2, column=1, padx=10, pady=5, sticky='w')

    return R1, R2

def VerboseCheckboxSettings(frame):
    global cveDesc
    global verboseGUI

    cveDesc = tk.IntVar()
    verboseGUI = tk. Checkbutton(frame, text='Include CVE description',variable=cveDesc, onvalue=2, offvalue=0)
    verboseGUI.grid(row=2, column=3, padx = 10, pady=5, sticky='w')
    verboseGUI.config(state=tk.DISABLED)

def StateVerbose():
    verboseGUI.config(state=tk.DISABLED if typeVariable.get() == 1 else tk.NORMAL)

def CreateCategories(frame):
    
    global checkboxList
    checkboxList = [] #Stores the variables assigned to the checkboxes - IMPORTANT, THIS IS WHERE THE STUFF HAPPENS
   
    categories = ['Damage to Property', "Loss of Productivity and Revenue", "Theft of Operational Information", "Compromise of Control", "Manipulation of Control",
                  "Compromise of View", "Manipulation of View", "Loss of Safety", 'Loss of Availability', "Societal Loss", "Environmental Loss"]
    cbvalue = [('None', 0), ('Low', 1), ('Medium', 2), ('High', 3), ('Critical', 4)]

    catLabel = tk.Label(frame, text="Check an impact severity box for each category")
    catLabel.pack()
    
    catFrame = tk.Frame(frame)
    catFrame.pack()

    for i, impactName in enumerate(categories):
        cat = tk.Label(catFrame, text = impactName)
        cat.grid(row=i,column=0, padx=10, pady=5, sticky='w')
        cbVar = tk.IntVar()

        for j, (severity, weight) in enumerate(cbvalue):
            
            checkbox = tk.Checkbutton(catFrame, text=severity, variable=cbVar, onvalue= weight, offvalue=0)
            checkbox.grid(row=i,column=j+1 )

        checkboxList.append(cbVar) 

def CalculateButton(frame):
    calculateButton = tk.Button(frame, text="Calculate risk", command=PerformCalc)#, command=performCalc
    calculateButton.grid(row=3, column=1, padx = 10, pady=5, sticky='w')
    

def test():
    print(f"{typeVariable.get()}, {cveDesc.get()}")  

def CreateTab1(notebook):

    padyValue = 3 # value used to pad the y axis, used to be more consistent
    tab1 = ttk.Frame(notebook)

    textTop = """How to use:
    1. Please select a PLC manufacturer and the industry of your organization from the corresponding dropdown menus
    2. Select the appropriate output type - 'Risk assessment only' is the default. If 'Verbose' selected, specify whether you want the CVE descriptions to be outputted
    3. Enter the model of the PLC in the search bar - do not include the name of the manufacturer
    4. Check the appropriate impact boxes based on the consequences as a result of a PLC attack"""
    tab1Label = tk.Label(tab1, text=textTop, justify=tk.LEFT)
    tab1Label.pack()
    

    # Create frames for left and right sides with borders
    leftFrame = tk.Frame(tab1, bd=1, relief=tk.SUNKEN)
    
    EntryBox(leftFrame).pack(pady = 10) #gets entry field

    leftLeftFrame = tk.Frame(leftFrame, bd=1)#, relief=tk.SUNKEN
    leftRightFrame = tk.Frame(leftFrame, bd=1, relief=tk.SUNKEN)

    # Left side UI elements
    IndustryDropdownSettings(leftLeftFrame)
    ManufacturerDropdownSettings(leftLeftFrame)

    RadioButtonSettings(leftLeftFrame)
    VerboseCheckboxSettings(leftLeftFrame)
    CalculateButton(leftLeftFrame)

    leftLeftFrame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')
    leftFrame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

    # Right side UI elements
    rightFrame = tk.Frame(tab1, bd=1, relief=tk.SUNKEN)
    CreateCategories(rightFrame)
    rightFrame.pack(side=tk.RIGHT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

    notebook.add(tab1, text="Individual PLC Calculation")
        
def CreateTab2(notebook):
    tab2 = ttk.Frame(notebook)

    notebook.add(tab2, text="Group PLC Calculation")

def CreateNotebook():
    notebook = ttk.Notebook(root)
    CreateTab1(notebook)
    CreateTab2(notebook)
    notebook.pack(expand=1, fill="both")

def main():
    CreateMenuBar()
    CreateFrame()
    CreateNotebook()
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
