import nvdlib

r = nvdlib.searchCVE(cpeName = 'cpe:2.3:h:siemens:simatic_s7-1200:-:*:*:*:*:*:*:*')
for eachCVE in r:
   print(eachCVE.id, str(eachCVE.score[0]), eachCVE.url)
# r = nvdlib.searchCPE(keywordSearch = 'simatic s7-1200')
# for eachCPE in r:
#     print(eachCPE.cpeName)