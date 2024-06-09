import nvdlib

# def main():
#     #test_model = "cpe:2.3:o:siemens:sinamics_sl150_firmware:4.7:-:*:*:*:*:*:*:*"
#     test_model = "simatic"
#     cve_list = searchNVDCPE(test_model)
    
#     if cve_list is not None:
#         for cve in cve_list:
#             print(cve)
#     else:
#         print("No CVEs found or an error occurred.")

# def searchNVDCPE(model):
#     print("searching")
#     try:
#       cveList = nvdlib.searchCPE(keywordSearch=model)
#         # if model.startswith("cpe:"):
#         #     cveList = nvdlib.searchCPE(cpeMatchString=model)
#         # else:
#         #     cveList = nvdlib.searchCPE(keywordSearch=model)
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None
#     return cveList

# if __name__ == "__main__":
#     main()

r = nvdlib.searchCPE(cpeMatchString='cpe:2.3:o:siemens:sinamics_sl150_firmware:4.7:-:*:*:*:*:*:*')
for eachCPE in r:
    print(eachCPE.cpeName)