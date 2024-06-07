# import tkinter as tk
# from tkinter import ttk, filedialog
# from logicgroup import *
# import threading
# from sharedvariables import calculationRunning
# import time

# def ImportFile():
#   # Open a file dialog for file selection
#   filePath = filedialog.askopenfilename(title="Select a file", filetypes=[("All files", "*.*")])

#   if filePath:
#     # User selected a file, perform actions with the file_path
#     print(f"Selected file: {filePath}")
#   else:
#     # User canceled file selection
#     print("File selection canceled")

# def FileSave():
#   # Implementation for the save button
#   tk.messagebox.showinfo("File Saved", "File saved")
#   print("Save button clicked")

# def HelpPopup():
#   # Implementation for the help button popup
     
#   popup = tk.Toplevel(root)
#   popup.title("How To Use")

#   intro = "Here is how you use ARC-C. Depending on whether you are calculating devices individually or in groups, the process will change."
#   introLabel = tk.Label(popup, text=intro, justify=tk.LEFT)
#   introLabel.pack(padx=10, pady=10)
#   #create notebook
#   notebook = ttk.Notebook(popup)
#   tab1 = tk.Frame(notebook)
#   notebook.add(tab1, text="Individual")
#   tab2 = tk.Frame(notebook)
#   notebook.add(tab2, text="Group")
#   notebook.pack(padx=10, fill='both', expand=True)

#   textTab1 = """How to use:
#   1. In the entry box, type in the name of the device you would like to analyse. The more specific you are, the easier it will be to find the appropriate device.
#   2. Select the appropriate output type:
#     'Risk assessment only' will provide a high level summarry of the risk analysis
#     'Verbose' will also include a list of all associated CVEs - this selection also provides the option to enable CVE descriptions in the output
#   3. Choose whether or not you want to modify the CVEs listed on a device - use this if specific CVEs have been patched
#   4. Choose whether or not you want to modify the CVSS base score of each CVE
#   5. Assign severities for each of the impact categories.
#   6. Press 'Calculate Risk' once you are ready to calculate.
#   If more than once device is found with the supplied name, a pop-up will appear. Select the specific device you require.
#   If 'Apply CVE patches' has been selected, a pop-up will appear. Choose the CVEs you do not want included in the calculation.
#   If 'Modify Base CVSS has been selected, a pop-up will appear. Choose the values which best suit your environement to modify the base score."""
#   labelTab1 = tk.Label(tab1, text=textTab1, justify=tk.LEFT)
#   labelTab1.pack(padx=10, pady=10)

#   textTab2 = """This will be used for the second tab."""
#   labelTab2 = tk.Label(tab2, text=textTab2, justify=tk.LEFT)
#   labelTab2.pack(padx=10, pady=10)


# def CreateMenuBar():
#   menuBar = tk.Menu(root)

#   # File Dropdown
#   fileMenu = tk.Menu(menuBar, tearoff=0)
#   fileMenu.add_command(label="Import", command=ImportFile)
#   fileMenu.add_command(label="Save", command=FileSave)
#   menuBar.add_cascade(label="File", menu=fileMenu)

#   # Help Button
#   menuBar.add_command(label="How To Use", command=HelpPopup)

#   root.config(menu=menuBar)

# cooldownTime = 10000 #how often you can call the API
# cooldownActive = False


# def main():
#   CreateMenuBar()
#   # Lock window resizing
#   root.resizable(False, False)
    
#   # Run the application
#   root.mainloop()

# def onClosing():
#   root.destroy()

# # Create the main window
# root = tk.Tk()
# root.title("ARC-C Risk Assessment Tool")
# root.geometry("1280x720")
# root.resizable(False, False)

# if __name__ == "__main__":
#   root.protocol('WM_DELETE_WINDOW', onClosing)
#   main()

