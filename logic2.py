import tkinter as tk
from nvd import *
from mitre import *
import re
from sharedvariables import calculationRunning
import threading

def CalculateRisk(entryField, industryDropdown, manufacturerDropdown, typeVariable, cveDesc, categoryList):
        global calculationRunning

        currentID = threading.current_thread().ident
        #currentID = currentThread.ident
        #print(currentID)
        # call functions from nvd and mitre
        # have sub functions for each call
        # as much abstraction as possible
        verbose = ""
        multiplier = 0
        attack = Attck()

        # use entry field as an argument for search

        searchTermList = getSearchTermList(entryField, manufacturerDropdown)
        resultTuple = searchPLCInfoNVD(entryField)
        damageToProperty = getImpactMultiplier(categoryList[0])
        internalOpLoss = getImpactMultiplier(categoryList[1])
        externalOpLoss = getImpactMultiplier(categoryList[2])
        opInfoTheft = getImpactMultiplier(categoryList[3])
        controlLoss = getImpactMultiplier(categoryList[4])
        viewLoss = getImpactMultiplier(categoryList[5])
        controlManipulation = getImpactMultiplier(categoryList[6])
        viewManipulation = getImpactMultiplier(categoryList[7])
        cveList = resultTuple[0]
        searchIndex = resultTuple[1]
        actorsList = getListOfActorsForIndustry(industryDropdown)

       
        errorNoCVE(cveList)  # check whether the cveList is empty - useless to continue if not
        
        if CheckStatus(calculationRunning, currentID): #if the thread was cancelled, don't do this
            RemovePatchedCVEs(cveList)
            #print(f'cve {calculationRunning}')
            # If verbose, generate verbose output
            if typeVariable == 2:
                if cveDesc == 2:
                    verbose = generateVerboseOutput(cveList, actorsList, True) # verbose + descritpion
                else: 
                    verbose = generateVerboseOutput(cveList, actorsList, False) # only verbose
                

            cvssScore = 0.0
            availabilityEff = 0.0
            confidentialityEff = 0.0
            integrityEff = 0.0
            exploitabilityScore = 0.0
            impactScore = 0.0
            numberVuln = len(cveList)
            actorsScore = getActorNumberRiskScore(actorsList)
            impactCat = damageToProperty * internalOpLoss * externalOpLoss * opInfoTheft * controlLoss * viewLoss * controlManipulation * viewManipulation

            for eachCVE in reversed(cveList):
                if getBaseScoreCVE(eachCVE) == -1:
                    # There is no base score for the CVE, likely very recent
                    # skip this CVE
                    continue
                else:
                    multiplier = getMultiplierCVE(eachCVE)
                    #cvssScore += float(getBaseScoreCVE(eachCVE))
                    #availabilityEff += getImpactConversion(getAvailabilityImpactCVE(eachCVE))  * multiplier
                    integrityEff += getImpactConversion(getIntegrityImpactCVE(eachCVE)) * multiplier
                    confidentialityEff += getImpactConversion(getConfidentialityImpactCVE(eachCVE)) * multiplier
                    exploitabilityScore += getExploitabilityScoreCVE(eachCVE) * multiplier
                    impactScore += getImpactScoreCVE(eachCVE) * multiplier

            # actorsScore += getActorScore(len(actorsList))


            #cvssScore /= numberVuln
            #availabilityEff /= numberVuln
            integrityEff /= numberVuln
            confidentialityEff /= numberVuln
            exploitabilityScore /= numberVuln
            impactScore /= numberVuln

            formulaRes = ((exploitabilityScore + confidentialityEff + integrityEff + impactScore) / 4 * actorsScore * impactCat) / 3

            totalRiskOutput = outputRiskInfo(industryDropdown, actorsList, exploitabilityScore, confidentialityEff, integrityEff, impactScore, 
                                             formulaRes, numberVuln, cpeOfficialName, typeVariable, verbose)
            DisplayRisk(totalRiskOutput)

        for tuple_entry in calculationRunning: #removes thread from calculationRunning
            if tuple_entry[1] == currentID:
                calculationRunning.remove(tuple_entry)
                break
##check to see if the current thread has been "canceled" or not
# array is the calculationRunning list which contains a tuple of the cancelation state and thread ID associated, threadID is the ID of the current thread
def CheckStatus(array, threadID): 
    for bool, int in array:
        if int == threadID:
            if bool:
                #print(f'{threadID} is active')
                bool = False
                return True 
    #print(f'{threadID} is inactive')
    return False

def RemovePatchedCVEs(cveList):
    popup = tk.Toplevel()
    popup.title("Checkbox Popup")
    popup.resizable(False, False)

    # Create a scrollbar
    scrollbar = tk.Scrollbar(popup)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    checkboxFrame = tk.Frame(popup)
    checkboxFrame.pack()

    checkboxCanvas = tk.Canvas(checkboxFrame, yscrollcommand=scrollbar.set)
    checkboxCanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar.config(command=checkboxCanvas.yview)

    checkboxInnerFrame = tk.Frame(checkboxCanvas)
    checkboxCanvas.create_window((0, 0), window=checkboxInnerFrame, anchor=tk.NW)

    checkboxes = []
    for cve in reversed(cveList):
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(checkboxInnerFrame, text=getCVE(cve), variable=var)
        checkbox.pack(anchor=tk.W)
        checkboxes.append((cve, var))

    def ApplyChanges():
        for item, var in checkboxes:
            if var.get():
                cveList.remove(item)
        #tk.messagebox.showinfo("Success", "Changes applied successfully")
        popup.destroy()

    applyButton = tk.Button(popup, text="Apply Changes", command=ApplyChanges)
    applyButton.pack()

    def OnConfigure(event):
        checkboxCanvas.configure(scrollregion=checkboxCanvas.bbox("all"))

    checkboxInnerFrame.bind("<Configure>", OnConfigure)

    popup.wait_window()

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

def outputRiskInfo(industryDropdown, actorsList, exploitabilityScore, confidentialityEff, integrityEff, impactScore, formulaRes, numberVuln, cpeOfficialName, selection, verbose):

    output = "The number of vulnerabilities for this PLC family is:\n"
    output += str(numberVuln) + "\n"
    output += "The risk score for this PLC family is:\n"
    output += str(round(formulaRes, 2)) + "\n"
    output += "The risk subscores for this PLC family are:\n"
    output += "Exploitability Score: " + str(round(exploitabilityScore, 2)) + "\n"
    output += "Confidentiality Score: " + str(round(confidentialityEff, 2)) + "\n"
    output += "Integrity Score: " + str(round(integrityEff, 2)) + "\n"
    output += "Impact Score: " + str(round(impactScore, 2)) + "\n"
    if formulaRes > 8:
        output += "Your device is at critical risk!\n"
        output += "Check vendor website for latest patches/guidance.\n"
        # if not verbose
        if selection != 4:
            output += "Try calculating risk with verbose output option\nselected for more information about this device.\n"
    elif formulaRes > 6:
        output += "Your device is at high risk!\n"
    elif formulaRes > 4:
        output += "Your device is at medium risk\n"
    else:
        output += "Your device is at low risk!\n"
    output += "The number of APTs that attack the " + industryDropdown + " industry: " + "\n"
    output += "The term we searched for is : " + cpeOfficialName + "\n" 
    # output += "The actors which attack the " + industryDropdown + "industry are\n"

#    for actor in actorsList:
#       output += str(actor) + "\n"

    # if verbose
    if selection == 2 or selection == 3:
        output += verbose
        # reset verbose for future queries
        verbose = ""

    return output

def generateVerboseOutput(cveList, actorsList, description):
    verbose = ""
    if (len(actorsList) > 0):
        verbose += "\nAPTs that are known to attack this industry:\n\n"
        verbose += "["
        for actor in actorsList:
            verbose += actor + ", "
        verbose = re.sub(r"..$", "] ", verbose)
        verbose += "\n\n"
    verbose += "Here is some information about the latest CVEs impacting this PLC family.\n\n"

    for eachCVE in reversed(cveList):
        if getBaseScoreCVE(eachCVE) == -1:
            # There is no base score for the CVE, likely very recent
            # skip this CVE
            continue           
        else:
            verbose += getCVE(eachCVE) + "\n\n"
            if description == True:
                verbose += "Description:\n" + getDescriptionCVE(eachCVE) + "\n\n"
            verbose += "Base Score: " + str(getBaseScoreCVE(eachCVE)) + "\n"
            verbose += "Availability Impact: " + str(getAvailabilityImpactCVE(eachCVE)) + "\n"
            verbose += "Confidentiality Impact: " + str(getConfidentialityImpactCVE(eachCVE)) + "\n"
            verbose += "Integrity Impact: " + str(getIntegrityImpactCVE(eachCVE)) + "\n"
            verbose += "Impact Score: " + str(getImpactScoreCVE(eachCVE)) + "\n"
            verbose += "Exploitability Score: " + str(getExploitabilityScoreCVE(eachCVE)) + "\n\n"
            verbose += "========================\n\n"

    return verbose


def CheckForError(entryField, manufacturerDropdownVal, categoryList):
    noError = True
    # if the manufacturer is Other and the field is empty we have nothing to search for
    if entryField.get() == "" and manufacturerDropdownVal == "Other":
        # pop up
        tk.messagebox.showerror("The PLC search field is empty!", "Unfortunately, we're not mind readers! Please input a PLC family in the search bar.")
        noError = False
    elif manufacturerDropdownVal == "Select PLC Manufacturer:":
        # pop up
        tk.messagebox.showerror("PLC manufacturer not selected!", "Please select a PLC manufacturer")
        noError = False
    else:
        for cat in categoryList:
            if cat == 0:
                noError = False
                tk.messagebox.showerror("Impact checkbox empty", "Please select a checkbox for each category")                
                break

    return noError

def errorNoCVE(cveList):
    if len(cveList) == 0:
        tk.messagebox.showerror("Search error!", "Apologies, we could not find any PLC model with the given name. Try modifying the input in the search field.")

def searchPLCInfoNVD(searchTermList):
    global cpeOfficialName
    cveList = []
    indexOfList = 0
    cpeList = searchNVDCPE(searchTermList)
    cpeName = chooseWhichCPE(cpeList)
    if cpeName:
        cpeOfficialName = cpeName.cpeName #THIS IS TEMP
        cveList = searchNVD(cpeName.cpeName)
    # for cpe in cveList:
    #     print(cpe.cpeName)
    # for searchTerm in searchTermList:
    #     cveList = searchNVDCPE(searchTerm)
    #     if len(cveList) != 0:
    #         indexOfList = searchTermList.index(searchTerm)
    #         break

    cveList2 = getLatestCVEList(cveList)
 
    return cveList2, indexOfList

def chooseWhichCPE(cpeList):
    selectedValue = None

    def on_button_click():
        nonlocal selectedValue
        selectedIndex = listbox.curselection()
        if selectedIndex:
            selectedValue = cpeList[selectedIndex[0]]
            popup.destroy()
            #print(f"Selected value: {selectedValue}")
            return selectedValue

    popup = tk.Toplevel()
    popup.title("Choose your CPE")
    popup.resizable(False, False)

    maxLength = max(len(cpe.cpeName) for cpe in cpeList)
    listbox = tk.Listbox(popup, width=maxLength + 2, height=20)  # Set the width based on the longest string
    for cpe in cpeList:
        listbox.insert(tk.END, cpe.cpeName)
    listbox.grid(row=0, column=0, pady=10, sticky=tk.NSEW)  # Use grid instead of pack

    scrollbar = tk.Scrollbar(popup, command=listbox.yview, width=20)  # Set the width of the scrollbar
    scrollbar.grid(row=0, column=1, sticky=tk.NS)  # Use grid for the scrollbar

    listbox.config(yscrollcommand=scrollbar.set)

    button = tk.Button(popup, text="Select", command=on_button_click)
    button.grid(row=1, column=0, columnspan=2, pady=10, sticky=tk.NSEW)  # Use grid for the button and set columnspan

    popup.wait_window()
    return selectedValue

def getSearchTermList(entryField, manufacturerDropdown):

    searchTermList = []

    # If manufacturer is Other then all search information is in the entryField
    if manufacturerDropdown == "Other":
        manufacturerDropdown = ""

    while (' ' in entryField) or ('-' in entryField):
        searchTermList.insert(0, str(manufacturerDropdown) + " " + entryField)
        entryField = re.split('-| ', entryField, 1)[0]

    # add last element in the string
    searchTermList.append(manufacturerDropdown + " " + entryField)

    # If manufacturer specified then add it as a last resort
    if manufacturerDropdown != "":
        searchTermList.append(str(manufacturerDropdown))

    return searchTermList

def getImpactMultiplier(category):
    multiplier = 1
    if category == 5:
        multiplier = 1
    elif category == 4:
        multiplier = 0.95
    elif category == 3:
        multiplier = 0.9
    elif category == 2:
        multiplier = 0.85
    elif category == 1:
        multiplier = 0.8
    return multiplier
