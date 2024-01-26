import nvdlib
from nvd import *
from datetime import datetime, timedelta, date
from cvsslib import cvss2, cvss31, calculate_vector
from cvsstesting import get_E_RL_RC
import tkinter as tk

#a = nvdlib.searchCVE(cveId = 'CVE-2017-12741')
r = [['V30', 7.5, 'HIGH'], 'CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H'], [['V31', 6.8, 'MEDIUM'], 'CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H']
#b = nvdlib.searchCVE(cveId = 'CVE-2019-13945')
#b = [['V31', 6.8, 'MEDIUM'], 'CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H']
#r = a + b
multiplier = 0
totalImpact = 0


def button_click():
  for eachCVE in r:
   #a = (getCVSS(eachCVE))
   #print(eachCVE[1])
   # a1 = str(a[1])
   b = get_E_RL_RC(root)
   final = '/' + '/'.join(b)
   d = eachCVE[1] + final
   print(calculate_vector(d, cvss31))
   #c = str(eachCVE[1]) + str(b
  #print(c)


# Create the main window
root = tk.Tk()
root.title("Button Example")

# Create a button
button = tk.Button(root, text="Click Me", command=button_click)
button.pack(pady=20)

# Run the Tkinter event loop
root.mainloop()


#    #print(eachCVE.metrics)
#    multiplier = getMultiplierCVE(eachCVE)
#    totalImpact += getCVSS(eachCVE)[0][1] * multiplier
#    # CVEYearString = eachCVE.published
#    # cveYear = datetime (int(CVEYearString[0:4]), int(CVEYearString[5:7]), int(CVEYearString[8:10]))
#    # currentYear = datetime.today()
#    # yearDelta = currentYear - cveYear
#    # print(f"{eachCVE.id}")
#    # print(f'cve {cveYear}, current {currentYear}, delta {yearDelta.days}')

#print(totalImpact)

# vector_v3 = "AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N/E:U/RL:W/RC:R/CR:H/IR:L/AR:X/MAV:X/MAC:L/MPR:X/MUI:N/MS:X/MC:L/MI:H/MA:H"
# print(calculate_vector(vector_v3, cvss31))



# r = nvdlib.searchCPE(keywordSearch = 'simatic s7-1200')
# for eachCPE in r:
#     print(eachCPE.cpeName)