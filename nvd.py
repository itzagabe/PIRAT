import nvdlib
import re
from datetime import datetime, timedelta, date
from nvdapikey import key
#name = input ("PLC product name ")
#cveList = nvdlib.searchCVE(keyword=name, limit=10)
#for eachCVE in cveList:
#   print (eachCVE.v3severity + " score:" + str(eachCVE.impact) + "\ndescription: " + str(eachCVE.cve.description.description_data[0].value) + "\n\n")

#riskScore = 0

#for eachCve in cveList:
#    if eachCve.impact.baseMetricV3.cvssV3.baseScore > 8:
#        riskScore = 10
#        break
#    elif eachCve.impact.baseMetricV3.cvssV3.baseScore > 6:
#        riskScore = 8
#       break

#print ("Risk score for this PLC is: " + str(riskScore))

# Find a way to pretty print this data
# Find a way to efficiently search for.
delay = 2

def searchNVDCPE(model):
    print(f"searching {model}")
    try:
        if model.startswith("cpe:"):
            model = model[:-2]
            cveList = nvdlib.searchCPE(cpeMatchString=model, key= key, delay = delay)
        else:
            cveList = nvdlib.searchCPE(keywordSearch=model, key= key, delay = delay)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return cveList


def searchNVD(cpe):
    print(f'searching cves for {cpe}')
    formatCPE = str(cpe)
    # find a way to securely store the key somewhere
    cveList = nvdlib.searchCVE(cpeName = formatCPE, key= key, delay = delay)#, keywordExactMatch= True) #added exact match
    return cveList

def getDescriptionCVE(cveItem):
    return str(cveItem.descriptions[0].value)

def getCVE(cveItem):
    return str(cveItem.id)

def getBaseScoreCVE(cveItem):
    if cveItem.score[1] is not None:
        return cveItem.score[1]
    else:
        return -1

def getAvailabilityImpactCVE(cveItem):
    try:
        return cveItem.metrics.cvssMetricV31[0].availabilityImpact
    except AttributeError:
        try:
            return cveItem.metrics.cvssMetricV30[0].availabilityImpact
        except AttributeError:
            try:
               return cveItem.metrics.cvssMetricV2[0].availabilityImpact
            except AttributeError:
               return 0
        
def getConfidentialityImpactCVE(cveItem):
    try:
        return cveItem.metrics.cvssMetricV31[0].confidentialityImpact
    except AttributeError:
        try:
            return cveItem.metrics.cvssMetricV30[0].confidentialityImpact
        except AttributeError:
            try:
               return cveItem.metrics.cvssMetricV2[0].confidentialityImpact
            except AttributeError:
               return 0
        
def getIntegrityImpactCVE(cveItem):
    try:
        return cveItem.metrics.cvssMetricV31[0].integrityImpact
    except AttributeError:
        try:
            return cveItem.metrics.cvssMetricV30[0].integrityImpact
        except AttributeError:
            try:
               return cveItem.metrics.cvssMetricV2[0].integrityImpact
            except AttributeError:
               return 0
        
def getImpactScoreCVE(cveItem):
    try:
        return cveItem.metrics.cvssMetricV31[0].impactScore
    except AttributeError:
        try:
            return cveItem.metrics.cvssMetricV30[0].impactScore
        except AttributeError:
            try:
               return cveItem.metrics.cvssMetricV2[0].impactScore
            except AttributeError:
               return 0

def getExploitabilityScoreCVE(cveItem):
    try:
        return cveItem.metrics.cvssMetricV31[0].exploitabilityScore
    except AttributeError:
        try:
            return cveItem.metrics.cvssMetricV30[0].exploitabilityScore
        except AttributeError:
            try:
               return cveItem.metrics.cvssMetricV2[0].exploitabilityScore
            except AttributeError:
               return 0
            
def getCVSS(cveItem):
    try:
        return cveItem.score, cveItem.v31vector
    except AttributeError:
        try:
            return cveItem.score, cveItem.v30vector 
        except AttributeError:
            try:
               return cveItem.score, cveItem.v2vector  
            except AttributeError:
               return 0

def getImpactConversion(cveWord):
    result = 0
    if cveWord == 'COMPLETE' or cveWord == 'HIGH':
        result = 10
    elif cveWord == 'PARTIAL' or cveWord == 'LOW':
        result = 6
    elif cveWord == 'NONE':
        result = 0
    return result

def getMultiplierCVE(cveItem):
    CVEYearString = cveItem.published
    cveYear = datetime(int(CVEYearString[0:4]), int(CVEYearString[5:7]), int(CVEYearString[8:10]))
    currentYear = datetime.today()
    yearDelta = (currentYear - cveYear).days // 365

    if yearDelta <= 0:
        return 1.0
    elif yearDelta <= 9:
        multiplier = 1.0 - (yearDelta * 0.1)
    else:
        multiplier = 0.1

    return multiplier

    # multiplier = 1
    # CVEYearString = cveItem.published
    # cveYear = datetime (int(CVEYearString[0:4]), int(CVEYearString[5:7]), int(CVEYearString[8:10]))
    # currentYear = datetime.today()
    # yearDelta = currentYear - cveYear
    # if int(yearDelta.days) <= 365:
    #     multiplier = 1
    # elif int(yearDelta.days) <= (2 * 365):
    #     multiplier = 0.9
    # elif int(yearDelta.days) <= (3 * 365):
    #     multiplier = 0.8
    # elif int(yearDelta.days) <= (4 * 365):
    #     multiplier = 0.7
    # elif int(yearDelta.days) <= (5 * 365):
    #     multiplier = 0.6
    # elif int(yearDelta.days) <= (6 * 365):
    #     multiplier = 0.5
    # elif int(yearDelta.days) <= (7 * 365):
    #     multiplier = 0.4
    # elif int(yearDelta.days) <= (8 * 365):
    #     multiplier = 0.3  
    # elif int(yearDelta.days) <= (9 * 365):
    #     multiplier = 0.2
    # else:
    #     multiplier = 0.1  

    # return multiplier

def getLatestCVEList(cveList):
    # Define the cutoff date
    cutoff_date = datetime.now() - timedelta(days=365 * 10)

    # Filter the list to include only CVEs that are not older than the cutoff date
    refined_cveList = [cve for cve in cveList if datetime.strptime(cve.published, '%Y-%m-%dT%H:%M:%S.%f') > cutoff_date]

    return refined_cveList
