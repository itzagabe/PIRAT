import tkinter as tk
from tkinter import ttk, filedialog
from logicgroup import *
import threading
from sharedvariables import calculationRunning
import time
from oldImpactLogic import CreateCategories, print_values

def onClosing():
  root.destroy()

def EntryBox(frame):
  global entryFieldIndividual
    
  entryLabel = tk.Label(frame, text="Enter the PLC model to analyze:")
  entryLabel.pack()
  entryVar = tk.StringVar()
  entryFieldIndividual = tk.Entry(frame, width=50, textvariable=entryVar)
  entryFieldIndividual.pack()

def LoadFile(frame):
  global entryFieldGroup
  entryFieldGroup = []
    
  def read_file_and_display():
    global entryFieldGroup
    entryFieldGroup = []
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    try:
      with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
          if not line.strip().startswith('#'):  # Check if the line starts with '#'
            entryFieldGroup.append(line.strip())
    except FileNotFoundError:
      print("File not found!")
    #print(entryFieldGroup)
  loadFile = tk.Button(frame, text="Load File", command=read_file_and_display)
  loadFile.pack()

def CreateTab2(notebook):
  tab2 = ttk.Frame(notebook)
  leftFrame = tk.Frame(tab2, bd=1, relief=tk.SUNKEN)
  EntryBox(leftFrame)#gets entry field
  leftFrame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')
  notebook.add(tab2, text="Individual Device Calculation")

def CreateTab1(notebook):

  padyValue = 3 # value used to pad the y axis, used to be more consistent
  tab1 = ttk.Frame(notebook)
  leftFrame = tk.Frame(tab1, bd=1, relief=tk.SUNKEN)
    
  LoadFile(leftFrame)#.pack(pady = 10) #gets entry field
  #CryptoEntry(leftFrame)
  leftFrame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

  notebook.add(tab1, text="Group Device Calculation")
        

def CreateShared():
  frame = tk.Frame(root, width=800, height=180, bd=1, relief=tk.SUNKEN)
  frame.pack(side=tk.TOP, fill=tk.X)
  mainFrame = tk.Frame(frame, bd=1, relief=tk.SUNKEN)

  leftFrame = tk.Frame(mainFrame)
  rightFrame = tk.Frame(mainFrame)

  leftFrame.pack(side=tk.LEFT, padx=10, pady=10)
  rightFrame.pack(side=tk.RIGHT, padx=10, pady=10)

  CreateCategories(leftFrame, rightFrame)
  printButton = tk.Button(mainFrame, text="Print Values", command=print_values)
  printButton.pack(pady=10)
  mainFrame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')

#Notebook implementation
# def CreateShared():
#     frame = tk.Frame(root, width=800, height=180, bd=1, relief=tk.SUNKEN)
#     frame.pack(side=tk.TOP, fill=tk.X)
    
#     mainFrame = tk.Frame(frame, bd=1, relief=tk.SUNKEN)
#     mainFrame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True, anchor='center')
    
#     notebook = ttk.Notebook(mainFrame)
    
#     leftFrame = tk.Frame(notebook)
#     rightFrame = tk.Frame(notebook)
    
#     notebook.add(leftFrame, text="Left Frame")
#     notebook.add(rightFrame, text="Right Frame")
#     notebook.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
#     CreateCategories(leftFrame, rightFrame)
    
#     printButton = tk.Button(mainFrame, text="Print Values", command=print_values)
#     printButton.pack(pady=10)

def CreateNotebook():
  def ChangedTab(event):
    global selectedTab
    selectedTab = notebook.index(notebook.select())
    print("Selected tab index:", selectedTab) #DEBUG

  notebook = ttk.Notebook(root)
  CreateTab2(notebook)
  CreateTab1(notebook)
  notebook.pack(expand=1, fill="both")
  notebook.bind("<<NotebookTabChanged>>", ChangedTab)


def main():
  CreateNotebook()
  CreateShared()
  
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
