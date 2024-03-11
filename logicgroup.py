import tkinter as tk
import math
from nvd import *
from mitre import *
import re
from sharedvariables import calculationRunning
import threading
from cvsslib import cvss2, cvss31, calculate_vector
from cvss import GetModifiedCVSS

def CalculateRisk(entryField, industryDropdown, typeVariable, cveDesc, applyPatch, modifyBaseCVSS, categoryList, dataCalc, cryptoEntry):
        global calculationRunning
        #entryField = ["simatic", "simatic s7"]
        currentID = threading.current_thread().ident
        #currentID = currentThread.ident
        #print(currentID)
        # call functions from nvd and mitre
        # have sub functions for each call
        # as much abstraction as possible
        

        def individualDevice():
          verbose = ""
          multiplier = 0
          resultTuple = searchPLCInfoNVD(entryField)
          if resultTuple[0] is None: #if no results are found, give error
              StopCalculation(currentID)
              return 
          
          cveList = resultTuple[0]

        
          errorNoCVE(cveList)  # check whether the cveList is empty - useless to continue if not
          
          if CheckStatus(calculationRunning, currentID): #if the thread was cancelled, don't do this
              # if apply patches checkmark - popup
              if applyPatch:
                  RemovePatchedCVEs(cveList)

              # If verbose, generate verbose output
              if typeVariable == 2:
                  if cveDesc == 2:
                      verbose = generateVerboseOutput(cveList, True) # verbose + descritpion
                  else: 
                      verbose = generateVerboseOutput(cveList, False) # only verbose
                  

              cvssScore = 0.0
              totalImpact = 0
              numberVuln = len(cveList)
              impactCat = GetImpact(categoryList, dataCalc) #this is the mitre impact calculation

              continueModifying = True #gets set to false

              for eachCVE in reversed(cveList):
                  if getBaseScoreCVE(eachCVE) == -1:
                      # There is no base score for the CVE, likely very recent
                      # skip this CVE
                      continue
                  else:
                      cveCVSS = getCVSS(eachCVE)
                      cveImpact = 0
                      if not cveCVSS[0][0] == 'V2' and modifyBaseCVSS and continueModifying:
                          impactScore, continueModifying = GetModifiedCVSS(eachCVE.id)
                          impactScore = '/' + '/'.join(impactScore)
                          impactScore = cveCVSS[1] + impactScore
                          impactScore = calculate_vector(impactScore, cvss31)[2]
                          #print(f'CVSS 3, {impactScore}')
                      else:
                          impactScore = getCVSS(eachCVE)[0][1]
                          
                          #debug code
                          if continueModifying:
                              print(f'CVSS 2, {impactScore}')
                          else:
                              print("Skipping over the rest")

                      multiplier = getMultiplierCVE(eachCVE)
                      totalImpact += impactScore * multiplier
              
              #print(totalImpact)
              # weighted total impact calculation
              if totalImpact > 10:
                  totalTemp = totalImpact - 10
                  totalTemp = math.sqrt(totalTemp)
                  totalImpact = 10 + totalTemp
                  #print(totalImpact)
                  if totalImpact > 20: 
                      totalImpact = 20

              formulaResult = (impactCat + totalImpact) #5#((exploitabilityScore + confidentialityEff + integrityEff + impactScore) / 4) / 3
              #formulaRes = ((exploitabilityScore + confidentialityEff + integrityEff + impactScore) / 4 * actorsScore * impactCat) / 3

              totalRiskOutput = outputRiskInfo(industryDropdown, totalImpact, 
                                              formulaResult, numberVuln, cpeOfficialName, impactCat, typeVariable, verbose)
              DisplayRisk(totalRiskOutput)

          StopCalculation(currentID) #clear thread once error
        
        def groupDevice():
          print(entryField)
          verbose = ""
          cveList = []
          multiplier = 0


          #First, get all CPEs for each device
          for index, field in enumerate(entryField):
            print(field)
            resultTuple = searchPLCInfoNVD(field, index + 1, len(entryField))
            if resultTuple[0] is None: #if no results are found, give error
                StopCalculation(currentID)
                return 
            
            cveList.append(resultTuple[0])
          
          errorNoCVE(cveList)  # check whether the cveList is empty - useless to continue if not
          
          completeImpact = 0
          totalCVEs = 0

          # Next, do the calculation
          for individualCVE in cveList:
            if CheckStatus(calculationRunning, currentID): #if the thread was cancelled, don't do this
                # if apply patches checkmark - popup
                if applyPatch:
                    RemovePatchedCVEs(individualCVE)
                  

                totalImpact = 0
                numberVuln = len(individualCVE)
                totalCVEs += numberVuln
                impactCat = GetImpact(categoryList, dataCalc) #this is the mitre impact calculation

                continueModifying = True #gets set to false

                for eachCVE in reversed(individualCVE):
                    if getBaseScoreCVE(eachCVE) == -1:
                        # There is no base score for the CVE, likely very recent
                        # skip this CVE
                        continue
                    else:
                        cveCVSS = getCVSS(eachCVE)
                        cveImpact = 0
                        if not cveCVSS[0][0] == 'V2' and modifyBaseCVSS and continueModifying:
                            impactScore, continueModifying = GetModifiedCVSS(eachCVE.id)
                            impactScore = '/' + '/'.join(impactScore)
                            impactScore = cveCVSS[1] + impactScore
                            impactScore = calculate_vector(impactScore, cvss31)[2]
                            #print(f'CVSS 3, {impactScore}')
                        else:
                            impactScore = getCVSS(eachCVE)[0][1]
                            
                            # #debug code
                            # if continueModifying:
                            #     print(f'CVSS 2, {impactScore}')
                            # else:
                            #     print("Skipping over the rest")

                        multiplier = getMultiplierCVE(eachCVE)
                        totalImpact += impactScore * multiplier
                
                #print(totalImpact)
                # weighted total impact calculation
                if totalImpact > 10:
                    totalTemp = totalImpact - 10
                    totalTemp = math.sqrt(totalTemp)
                    totalImpact = 10 + totalTemp
                    #print(totalImpact)
                    if totalImpact > 20: 
                        totalImpact = 20
                completeImpact += totalImpact
          completeImpact = completeImpact / len(cveList)
          formulaResult = (impactCat + completeImpact) #5#((exploitabilityScore + confidentialityEff + integrityEff + impactScore) / 4) / 3

          if not cryptoEntry:
            print('no')
          else: 
            print('yes')

          totalRiskOutput = outputRiskInfoGroup(len(entryField), completeImpact, 
                                          formulaResult, totalCVEs, impactCat, typeVariable, verbose)
          DisplayRisk(totalRiskOutput)
          
          StopCalculation(currentID) #clear thread once error
          

        if not isinstance(entryField, list):
            individualDevice()
        else:
            groupDevice()

        

def GetImpact(checkboxList, dataCalc):
    global impactTotal

    impactTotal = 0 #default impact - nothing

    for impact in checkboxList:
        impactTotal += getImpactMultiplier(impact.get())
    
    impactTotal += dataCalc

    if impactTotal:
        impactTotal /= len(checkboxList)

    

    return impactTotal        

def StopCalculation(currentID):
    print(f"Thread {currentID} aborted/completed")
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
        checkbox = tk.Checkbutton(checkboxInnerFrame, text=cve.id, variable=var)
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

def outputRiskInfoGroup(numOfDevices, totalImpact, formulaRes, numberVuln, impactCat, selection, verbose):

    output = "The number of devices in this group is: " + str(numOfDevices) + "\n" 
    output += "The number of vulnerabilities for this PLC family is:\n"
    output += str(numberVuln) + "\n"
    output += "The risk score for this PLC family is:\n"
    output += str(round(formulaRes, 2)) + "\n"
    output += "The risk subscores for this PLC family are:\n"
    output += "CVSS Score: " + str(round(totalImpact, 2)) + "\n"
    output += "MITRE Impact Risk Score: " + str(round(impactCat, 2)) + "\n"
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

    # if verbose
    if selection == 2 or selection == 3:
        output += verbose
        # reset verbose for future queries
        verbose = ""

    return output

def outputRiskInfo(industryDropdown, totalImpact, formulaRes, numberVuln, cpeOfficialName, impactCat, selection, verbose):

    output = "The number of vulnerabilities for this PLC family is:\n"
    output += str(numberVuln) + "\n"
    output += "The risk score for this PLC family is:\n"
    output += str(round(formulaRes, 2)) + "\n"
    output += "The risk subscores for this PLC family are:\n"
    output += "CVSS Score: " + str(round(totalImpact, 2)) + "\n"
    output += "MITRE Impact Risk Score: " + str(round(impactCat, 2)) + "\n"
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

    # if verbose
    if selection == 2 or selection == 3:
        output += verbose
        # reset verbose for future queries
        verbose = ""

    return output

def generateVerboseOutput(cveList, description):
    verbose = ""
    verbose += "Here is some information about the latest CVEs impacting this PLC family.\n\n"

    for eachCVE in reversed(cveList):
        if getBaseScoreCVE(eachCVE) == -1:
            # There is no base score for the CVE, likely very recent
            # skip this CVE
            continue           
        else:
            verbose += eachCVE.id + "\n\n"
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


def CheckForError(entryField, categoryList):
    noError = True
    # if the manufacturer is Other and the field is empty we have nothing to search for
    if entryField == "":
        # pop up
        tk.messagebox.showerror("The PLC search field is empty!", "Unfortunately, we're not mind readers! Please input a PLC family in the search bar.")
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

def searchPLCInfoNVD(searchTermList, currentDeviceNumber=None, totalDevicenumber=None):
    global cpeOfficialName
    cveList = []
    indexOfList = 0
    cpeList = searchNVDCPE(searchTermList)
    if cpeList is None:
        tk.messagebox.showerror("Error", "An error has occurred - please be more specific with your search")
        #print("An error has occurred - no CPEs were found")
        return None, None
    
    #used to tell the popup how many devices in group
    if currentDeviceNumber is None:
      cpeName = chooseWhichCPE(cpeList)
    else:
      cpeName = chooseWhichCPE(cpeList, currentDeviceNumber, totalDevicenumber)


    if cpeName:
        cpeOfficialName = cpeName.cpeName #THIS IS TEMP
        cveList = searchNVD(cpeName.cpeName)
    else:
        #print('An error has occured - a CPE was not selected')
        tk.messagebox.showerror("Error", 'An error has occured - a CPE was not selected')
        return None, None
    # for cpe in cveList:
    #     print(cpe.cpeName)
    # for searchTerm in searchTermList:
    #     cveList = searchNVDCPE(searchTerm)
    #     if len(cveList) != 0:
    #         indexOfList = searchTermList.index(searchTerm)
    #         break

    cveList2 = getLatestCVEList(cveList)
 
    return cveList2, indexOfList

def chooseWhichCPE(cpeList, currentDeviceNumber=None, totalDevicenumber=None):
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
    if currentDeviceNumber is None:
      popup.title("Choose your CPE")
    else:
      popup.title(f"Choose your CPE - ({currentDeviceNumber}/{totalDevicenumber})")
    popup.resizable(False, False)

    maxLength = max(len(cpe.cpeName) for cpe in cpeList)
    listbox = tk.Listbox(popup, width=maxLength + 2, height=20)
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
    if category == 4:
        return 10
    elif category == 3:
        return 7
    elif category == 2:
        return 4
    elif category == 1:
        return 2
    elif category == 0:
        return 0
    else:
        return 0
