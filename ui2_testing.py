import tkinter as tk
from tkinter import ttk, filedialog
from logic2 import *
import threading
from sharedvariables import calculationRunning
import time

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
    tk.messagebox.showinfo("File Saved", "File saved")
    print("Save button clicked")

def HelpPopup():
    # Implementation for the help button popup
     
    popup = tk.Toplevel(root)
    popup.title("How To Use")

    intro = "Here is how you use PIRAT. Depending on whether you are calculating devices individually or in groups, the process will change."
    introLabel = tk.Label(popup, text=intro, justify=tk.LEFT)
    introLabel.pack(padx=10, pady=10)
    #create notebook
    notebook = ttk.Notebook(popup)
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text="Individual")
    tab2 = tk.Frame(notebook)
    notebook.add(tab2, text="Group")
    notebook.pack(padx=10, fill='both', expand=True)

    textTab1 = """How to use:
    1. In the entry box, type in the name of the device you would like to analyse. The more specific you are, the easier it will be to find the appropriate device.
    2. Select the appropriate output type:
        'Risk assessment only' will provide a high level summarry of the risk analysis
        'Verbose' will also include a list of all associated CVEs - this selection also provides the option to enable CVE descriptions in the output
    3. Choose whether or not you want to modify the CVEs listed on a device - use this if specific CVEs have been patched
    4. Assign severities for each of the impact categories.
    5. Press 'Calculate Risk' once you are ready to calculate.
        If more than once device is found with the supplied name, a pop-up will appear. Select the specific device you require.
        If 'Apply CVE patches' has been selected, a pop-up will appear. Choose the CVEs you do not want included in the calculation."""
    labelTab1 = tk.Label(tab1, text=textTab1, justify=tk.LEFT)
    labelTab1.pack(padx=10, pady=10)

    textTab2 = """This will be used for the second tab."""
    labelTab2 = tk.Label(tab2, text=textTab2, justify=tk.LEFT)
    labelTab2.pack(padx=10, pady=10)


def CreateMenuBar():
    menuBar = tk.Menu(root)

    # File Dropdown
    fileMenu = tk.Menu(menuBar, tearoff=0)
    fileMenu.add_command(label="Import", command=ImportFile)
    fileMenu.add_command(label="Save", command=FileSave)
    menuBar.add_cascade(label="File", menu=fileMenu)

    # Help Button
    menuBar.add_command(label="How To Use", command=HelpPopup)

    root.config(menu=menuBar)

cooldownTime = 10000 #how often you can call the API
cooldownActive = False

def PerformCalcInit():
    global cooldownActive
    # print('hi')
    # tempImpact(checkboxList)
    # return
    if CheckForError(entryField, checkboxList):
        if cooldownActive: #if you called the API recently, enact a cooldown
            return
        calculateButton.config(state=tk.DISABLED)
        cancelButton.config(state=tk.NORMAL)
        calcThread = threading.Thread(target=PerformCalc)
        calcThread.setDaemon(True) #allows you to close program if thread is active
        calcThread.start()
        calculationRunning.append([True, calcThread.ident])
        root.after(cooldownTime, EnableButton) #enable the button after x amount of time
        cooldownActive = True

def EnableButton():
    global cooldownActive, calculateButton
    
    if calculationRunning and not calculationRunning[-1][0]: #if the cooldown is over and no calculation is running, enable the button
        calculateButton.config(state=tk.NORMAL)
    cooldownActive = False

# def ShowCooldownMessage(seconds_left): #not used currently - add code to coolDownActive in performcalcinit if you want to dispaly text
#     tk.messagebox.showinfo("Cooldown", f"Button on cooldown. {seconds_left} seconds left.")
        
def PerformCalc():
    CalculateRisk(entryField.get(), industryVariable.get(), typeVariable.get(), cveDesc.get(), applyPatch.get(), checkboxList)
    #DisplayRisk(risk)
    #calculationRunning.pop()
    calculateButton.config(state=tk.NORMAL)

def UpdateCooldown(seconds_left):
    if seconds_left > 0:
        #ShowCooldownMessage(seconds_left)
        root.after(1000, UpdateCooldown, seconds_left - 1)

def CancelCalc():
    if calculationRunning:
        calculationRunning[-1] = [False, calculationRunning[-1][1]]
    if not cooldownActive: #if there is no cooldown, enable the calculate button again
        calculateButton.config(state=tk.NORMAL)
    cancelButton.config(state=tk.DISABLED)

def onClosing():
    if calculationRunning and calculationRunning[-1][0]: #only allow to close if no calcualtion is running
        tk.messagebox.showinfo("Calculation in Progress", "Please wait for the calculation to complete before closing.")
    else:
        root.destroy()

def CreateFrame():
    frame = tk.Frame(root, width=400, height=180, bd=1, relief=tk.SUNKEN)
    frame.pack(side=tk.TOP, fill=tk.X)

    # Welcome message
    bold1Label = tk.Label(frame, text="Welcome to PIRAT - Python Integrated Risk Assessment Tool!", font=('TkDefaultFont', 12, 'bold'), anchor='center')
    bold1Label.pack(pady=5)
    text1Label = tk.Label(frame, text="This tool allows you to estimate the risk of compromise of PLC devices by using the information from the National Vulnerability Database (NVD) and the MITRE ATT&CK Framework.", justify=tk.LEFT)
    text1Label.pack(padx=10, pady=5, anchor='w')
    bold2Label = tk.Label(frame, text="How do we do it?", font=('TkDefaultFont', 10, 'bold'), anchor='center')
    bold2Label.pack(pady=5)
    text2_label = tk.Label(frame, text="We process the information from the NVD and MITRE ATT&CK databases and feed it to our risk assessment formula to determine the risk factor of the PLC devices.", justify=tk.LEFT)
    text2_label.pack(padx=10, pady=5, anchor='w')

    return frame

# def OnEntryClick(event):
#     event.widget.delete(0, tk.END)

def EntryBox(frame):
    global entryField
    
    entryLabel = tk.Label(frame, text="Enter the PLC model to analyze:")
    entryLabel.pack()
    entryVar = tk.StringVar()
    #entryVar.set("Enter the PLC model to analyze:")
    entryField = tk.Entry(frame, width=50, textvariable=entryVar)
    entryField.pack()
    # entryField.bind("<Button-1>", OnEntryClick)
    # return entryField


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

def AppplyPatchCheckbox(frame):
    global applyPatch
    global applyCheckbox

    applyPatch = tk.IntVar()
    applyCheckbox = tk. Checkbutton(frame, text='Apply CVE patches', variable=applyPatch, onvalue=2, offvalue=0)
    applyCheckbox.grid(row=1, column=2, padx = 10, pady=5, sticky='w')
    #applyCheckbox.config(state=tk.DISABLED)

def VerboseCheckboxSettings(frame):
    global cveDesc
    global verboseGUI

    cveDesc = tk.IntVar()
    verboseGUI = tk. Checkbutton(frame, text='Include CVE description',variable=cveDesc, onvalue=2, offvalue=0)
    verboseGUI.grid(row=2, column=2, padx = 10, pady=5, sticky='w')
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
    global calculateButton
    global cancelButton

    calculateButton = tk.Button(frame, text="Calculate risk", command=PerformCalcInit)#, command=performCalc
    calculateButton.grid(row=3, column=1, padx = 10, pady=5, sticky='w')
    cancelButton = tk.Button(frame, text="Cancel", command=CancelCalc)
    cancelButton.config(state=tk.DISABLED)
    cancelButton.grid(row=3, column=2, padx=10, pady=5, sticky='w')

# def test(frame):
#     test1 = tk.Button(frame, text="test", command=test2)
#     test1.grid(row=4, column=2, padx=10, pady=5, sticky='w')
#     #print(f"{typeVariable.get()}, {cveDesc.get()}")  

# def test2():
#     print(calculationRunning)
    
def CreateTab1(notebook):

    padyValue = 3 # value used to pad the y axis, used to be more consistent
    tab1 = ttk.Frame(notebook)

    # textTop = """How to use:
    # 1. In the entry box, type in the name of the device you would like to analyse. The more specific you are, the easier it will be to find the appropriate device.
    # 2. Select the appropriate output type:
    #     'Risk assessment only' will provide a high level summarry of the risk analysis
    #     'Verbose' will also include a list of all associated CVEs - this selection also provides the option to enable CVE descriptions in the output
    # 3. Choose whether or not you want to modify the CVEs listed on a device - use this if specific CVEs have been patched
    # 4. Assign severities for each of the impact categories.
    # 5. Press 'Calculate Risk' once you are ready to calculate.
    #     If more than once device is found with the supplied name, a pop-up will appear. Select the specific device you require.
    #     If 'Apply CVE patches' has been selected, a pop-up will appear. Choose the CVEs you do not want included in the calculation."""
    # tab1Label = tk.Label(tab1, text=textTop, justify=tk.LEFT)
    # tab1Label.pack()
    

    # Create frames for left and right sides with borders
    leftFrame = tk.Frame(tab1, bd=1, relief=tk.SUNKEN)
    
    EntryBox(leftFrame)#.pack(pady = 10) #gets entry field

    leftLeftFrame = tk.Frame(leftFrame, bd=1)#, relief=tk.SUNKEN
    leftRightFrame = tk.Frame(leftFrame, bd=1, relief=tk.SUNKEN)

    # Left side UI elements
    IndustryDropdownSettings(leftLeftFrame)
    #ManufacturerDropdownSettings(leftLeftFrame)

    RadioButtonSettings(leftLeftFrame)
    VerboseCheckboxSettings(leftLeftFrame)
    AppplyPatchCheckbox(leftLeftFrame)
    CalculateButton(leftLeftFrame)
    #test(leftLeftFrame)

    leftLeftFrame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')
    leftFrame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

    # Right side UI elements
    rightFrame = tk.Frame(tab1, bd=1, relief=tk.SUNKEN)
    CreateCategories(rightFrame)
    rightFrame.pack(side=tk.RIGHT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

    notebook.add(tab1, text="Individual Device Calculation")
        
def CreateTab2(notebook):
    tab2 = ttk.Frame(notebook)

    textTop = """How to use:
    1. Please select a PLC manufacturer and the industry of your organization from the corresponding dropdown menus
    2. Select the appropriate output type - 'Risk assessment only' is the default. If 'Verbose' selected, specify whether you want the CVE descriptions to be outputted
    3. Enter the model of the PLC in the search bar - do not include the name of the manufacturer
    4. Check the appropriate impact boxes based on the consequences as a result of a PLC attack"""
    tab2Label = tk.Label(tab2, text=textTop, justify=tk.LEFT)
    tab2Label.pack()
    

    # # Create frames for left and right sides with borders
    # leftFrame = tk.Frame(tab2, bd=1, relief=tk.SUNKEN)
    
    # EntryBox(leftFrame).pack(pady = 10) #gets entry field

    # leftLeftFrame = tk.Frame(leftFrame, bd=1)#, relief=tk.SUNKEN
    # leftRightFrame = tk.Frame(leftFrame, bd=1, relief=tk.SUNKEN)

    # # Left side UI elements
    # IndustryDropdownSettings(leftLeftFrame)
    # ManufacturerDropdownSettings(leftLeftFrame)

    # RadioButtonSettings(leftLeftFrame)
    # VerboseCheckboxSettings(leftLeftFrame)
    # CalculateButton(leftLeftFrame)

    # leftLeftFrame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')
    # leftFrame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

    # # Right side UI elements
    # rightFrame = tk.Frame(tab2, bd=1, relief=tk.SUNKEN)
    # #CreateCategories(rightFrame)
    # rightFrame.pack(side=tk.RIGHT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')
    notebook.add(tab2, text="Group Device Calculation")

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
root.title("PIRAT - Risk Assessment Tool")
root.geometry("1280x720")
root.resizable(False, False)

if __name__ == "__main__":
    root.protocol('WM_DELETE_WINDOW', onClosing)
    main()
