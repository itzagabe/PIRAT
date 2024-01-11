from tkinter import *
from logic import *


class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='640x480+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)          
        master.title("PIRAT - Python Risk Assessment Tool")
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom

def performCalc():
    global entryField
    global industryVariable
    global manufacturerVariable
    global selection, cat1, cat2, cat3, cat4, cat5, cat6, varDesc
    if selection == 2 and varDesc.get() == 3:
        # if the selection is verbose and the description checkmark has been checked
        selection = 3
    elif selection == 3 and varDesc.get() == 0:
        # if we have unchecked the description checkmark
        selection = 2
    categoryList = [cat1, cat2, cat3, cat4, cat5, cat6, cat7, cat8]
    if checkForError(entryField, manufacturerVariable.get(), selection, categoryList):
        risk = calculateRisk(entryField.get(), industryVariable.get(), manufacturerVariable.get(), selection, categoryList)
        displayRisk(risk)

def displayRisk(riskVal):
    win = Toplevel()
    win.wm_title("Risk evaluation")
    win.geometry("850x500")

    # Create text widget and specify size.
    outputBox = Text(win)
    outputBox.place(relx = 0, rely = 0, width = 850, height = 500)
    # Scroll bar
    bar = Scrollbar(outputBox)
    bar.pack(side = RIGHT, fill = Y)

    outputBox.config(font=('Courier New',18,'bold'), yscrollcommand = bar.set)
    
    # Insert output into textbox.
    outputBox.insert(END, riskVal)

def deleteField(self):
    global firstClick
    if firstClick:
        entryField.delete(0, END)
        firstClick = False

def welcomeLabelSettings():
    headText = "Welcome to PIRAT - Python Risk Assessment Tool!\n"
    firstLine = "This tool allows you to estimate the risk of compromise of PLC devices by using the information\nfrom the National Vulnerability Database (NVD) and the MITRE ATT&CK Framework\n"
    nextLine = "How do we do it?\nWe process the information from the NVD and MITRE ATT&CK databases and feed it to our risk assessment formula to\n determine the risk factor of the PLC devices"
    welcomeLabel = Label(root, text = headText + firstLine + nextLine, font=("Arial", 22), bg="red")
    welcomeLabel.place(relx = 0.05, rely = 0.05, width=1500, height = 220)
    return welcomeLabel

def instructionLabelSettings():
    instText = "How to use:\n"
    instText += "1. Please select a PLC manufacturer and the industry of your organization from the corresponding dropdown menus\n"
    instText += "2. Select the appropriate output type - 'Risk assessment only' is the default. If 'Verbose' selected, specify whether you want the CVE descriptions to be outputted\n"
    instText += "3. Enter the model of the PLC in the search bar - do not include the name of the manufacturer\n"
    instText += "4. Check the appropriate impact boxes based on the consequences as a result of a PLC attack\n"
    instructionLabel = Label(root, text=instText, font=("Arial", 18))
    instructionLabel.place(relx = 0.12, rely = 0.29)
    return instructionLabel

def entryFieldSettings():
    entryField = Entry(root)
    entryField.insert(0, "Enter the PLC model to analyze:")
    entryField.bind("<ButtonPress-1>", deleteField)
    entryField.place(relx = 0.20, rely = 0.44, width = 500)
    return entryField

def industryDropdownSettings():
    OPTIONS = ["Aerospace","Chemical","Cyber","IT","Health","Law","Manufacturing","Maritime","Military",
               "Gambling", "Education","Finance","Government","Defense","Energy", "Engineering",
               "Petroleum","Retail","Technology","Telecom","Transportation"]
    OPTIONS = sorted(OPTIONS)

    industryVariable = StringVar(root)
    industryVariable.set("Select industry:") # default value

    industryDropdown = OptionMenu(root, industryVariable, *OPTIONS)
    industryDropdown.place(relx = 0.20, rely = 0.49, width = 230)
    return industryVariable

def manufacturerDropdownSettings():
    OPTIONS = ["ABB","Allen Bradley","Beckhoff","Delta","Eaton","Fatek","Festo",
               "Fuji","GeFanuc","Hitachi","Honeywell","Inovance","Kinco","LG",
               "Mitsubishi","Omron","Panasonic","Schneider Electric","Siemens",
               "Toshiba","Unitronics","Wago","Yokogawa","Other"]

    manufacturerVariable = StringVar(root)
    manufacturerVariable.set("Select PLC Manufacturer:") # default value

    manufacturerDropdown = OptionMenu(root, manufacturerVariable, *OPTIONS)
    manufacturerDropdown.place(relx = 0.20, rely = 0.52, width = 230)
    return manufacturerVariable

def selectOutputType():
    global selection
    global var
    selection = var.get()

def radioButtonSettings():
    radioLabel = Label(root, text="Select type of output:")
    radioLabel.place (relx = 0.34, rely = 0.47)

    R1 = Radiobutton(root, text="Risk assessment only", variable=var, value=1,
                     command=selectOutputType)
    R1.place(relx = 0.34, rely = 0.495)
    var.set(1)

    # Verbose will output CVE description + any relevant MITRE ATT&CK info
    R2 = Radiobutton(root, text="Verbose", variable=var, value=2,
                     command=selectOutputType)
    R2.place(relx = 0.34, rely = 0.52)

def checkboxMatrixSettings():
    checkLabel = Label(root, text = "Check one impact severity box for each category:")
    checkLabel.place(relx = 0.60, rely = 0.41)
    create_categories()

def create_categories():
    
    global cbVariableList

    checkboxList = [] #Stores the checkboxes
    cbVariableList = [] #Stores the variables assigned to the checkboxes - IMPORTANT, THIS IS WHERE THE STUFF HAPPENS
    
    #Location of Values
    defaultPosY = 0.44 
    defaultPosX = 0.60
    
    categories = ['Damage to Property', "Loss of Productivity and Revenue", "Theft of Operational Information", "Compromise of Control", "Manipulation of Control",
                  "Compromise of View", "Manipulation of View", "Loss of Safety", 'Loss of Availability', "Societal Loss", "Environmental Loss"]
    cbvalue = [('None', 0), ('Low', 1), ('Medium', 2), ('High', 3), ('Critical', 4)]

    for i, impactName in enumerate(categories):
        cat = Label(root, text = impactName)
        cat.place(relx = 0.50, rely = defaultPosY + (i * 0.03))
        cbVar = IntVar()
        print("")
        print(f'{impactName}: ' , end = " ")
        for j, (severity, weight) in enumerate(cbvalue):
            print(f'{severity} ({weight})', end = " ")
            
            checkbox = Checkbutton(root, text=severity, variable=cbVar, onvalue= weight, offvalue=0, command=checkboxSelection)
            checkbox.place(relx= defaultPosX + (j * 0.05), rely= defaultPosY + (i * 0.03))
            checkboxList.append(checkbox)
        
        #cbVar.set(0)
        cbVariableList.append(cbVar)
    #checkboxSelection()

def checkboxSelection():
    print("test")
    

    updatedCategories.clear()

    for var in cbVariableList:
        updatedCategories.append(var.get())

    for boop in updatedCategories:
        print(boop, end = " ")

def verboseCheckboxSettings():
    cDesc = Checkbutton(root, text='Include CVE description',variable=varDesc, onvalue=3, offvalue=0)
    cDesc.place(relx = 0.39, rely=0.52)
        
def buttonSettings():
    calculateButton = Button(root, text="Calculate risk", command=performCalc)
    calculateButton.place(relx = 0.30, rely = 0.56, width = 200, height = 40)

root = Tk()
app = FullScreenApp(root)

global updatedCategories
updatedCategories = [] #should probably initialize global variable somewhere else
firstClick = True
selection = 1
cat1 = 0
cat2 = 0
cat3 = 0
cat4 = 0
cat5 = 0
cat6 = 0
cat7 = 0
cat8 = 0
var = IntVar()
var1 = IntVar()
var2 = IntVar()
var3 = IntVar()
var4 = IntVar()
var5 = IntVar()
var6 = IntVar()
var7 = IntVar()
var8 = IntVar()
varDesc = IntVar()

welcomeLabel = welcomeLabelSettings()

instructionLabel = instructionLabelSettings()

entryField = entryFieldSettings()

calculateButton = buttonSettings()

industryVariable= industryDropdownSettings()

manufacturerVariable = manufacturerDropdownSettings()

checkboxVariable = checkboxMatrixSettings()

radioButtonSettings()

verboseCheckboxSettings()


root.mainloop()
