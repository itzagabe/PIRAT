import tkinter as tk
from logicgroup import *

def toggle_subcategories(category_idx, subcat_labels1, subcat_checkbuttons1, toggle_buttons1, category_checkbuttons1, subcat_labels2, subcat_checkbuttons2, toggle_buttons2, category_checkbuttons2):
    category_label = categories[category_idx][0]

    def toggle_set(subcat_labels, subcat_checkbuttons, toggle_buttons, category_checkbuttons):
        if subcat_labels[category_idx][0].winfo_ismapped():
            for label in subcat_labels[category_idx]:
                label.grid_remove()
            for checkbutton_row in subcat_checkbuttons[category_idx]:
                for checkbutton in checkbutton_row:
                    checkbutton.grid_remove()
            toggle_buttons[category_idx].config(text="►")
            # Re-enable the category checkboxes
            for checkbox in category_checkbuttons[category_idx]:
                checkbox.config(state=tk.NORMAL)
            # Update active status
            active_status[category_label] = "Active"
            for subcat in subcat_labels[category_idx]:
                active_status[subcat.cget("text").strip()] = "Inactive"
        else:
            for label in subcat_labels[category_idx]:
                label.grid()
            for checkbutton_row in subcat_checkbuttons[category_idx]:
                for checkbutton in checkbutton_row:
                    checkbutton.grid()
            toggle_buttons[category_idx].config(text="▼")
            # Disable the category checkboxes
            for checkbox in category_checkbuttons[category_idx]:
                checkbox.config(state=tk.DISABLED)
            # Update active status
            active_status[category_label] = "Inactive"
            for subcat in subcat_labels[category_idx]:
                active_status[subcat.cget("text").strip()] = "Active"

    toggle_set(subcat_labels1, subcat_checkbuttons1, toggle_buttons1, category_checkbuttons1)
    toggle_set(subcat_labels2, subcat_checkbuttons2, toggle_buttons2, category_checkbuttons2)

def print_values():
    severity_mapping = {0: "None", 1: "Low", 2: "Medium", 3: "High"}
    activeCategories = []
    for label, cbVar in checkboxList:
        if active_status[label] == "Active":
            activeCategories.append(f"{label}, {severity_mapping[cbVar.get()]}")
    for item in activeCategories:
        print(item)
    print('')

def CreateCategories(frame1, frame2):
    global checkboxList, active_status, categories
    checkboxList = []  # Stores the (label, variable) tuples
    active_status = {}  # Stores the active status of categories and subcategories

    categories = [('Safety', []), ('Loss', ['Societal', 'Environmental']), ('Theft', ['Operational', 'IP'])]
    cbvalue = [('None', 0), ('Low', 1), ('Medium', 2), ('High', 3)]

    def create_frame_widgets(frame, subcat_labels, subcat_checkbuttons, toggle_buttons, category_checkbuttons, label_text):
        catLabel = tk.Label(frame, text=label_text, anchor='w')
        catLabel.pack(fill='x')
        
        catFrame = tk.Frame(frame)
        catFrame.pack(fill='x')

        # Calculate maximum severity name length
        max_severity_length = max(len(severity) for severity, _ in cbvalue)

        # Set fixed width for the label column
        label_column_width = max(max_severity_length, 12)  # Adjust this value as needed

        # Create labels for severity ratings at the top with fixed width
        for j, (severity, weight) in enumerate(cbvalue):
            severity_label = tk.Label(catFrame, text=severity, width=max_severity_length, anchor='w')
            severity_label.grid(row=0, column=j+3, padx=3, pady=5, sticky='w')  # Shifted by one column

        current_row = 1
        for i, (impactName, subcategories) in enumerate(categories):
            active_status[impactName] = "Active"  # Initialize active status
            row_idx = current_row
            if subcategories:
                toggle_button = tk.Button(catFrame, text="►", command=lambda idx=i: toggle_subcategories(idx, subcat_labels1, subcat_checkbuttons1, toggle_buttons1, category_checkbuttons1, subcat_labels2, subcat_checkbuttons2, toggle_buttons2, category_checkbuttons2), width=2)
                toggle_button.grid(row=row_idx, column=0, padx=10, pady=5, sticky='w')
                toggle_buttons.append(toggle_button)
            else:
                toggle_buttons.append(None)
                # empty_label = tk.Label(catFrame, text="  ", width=2)
                # empty_label.grid(row=row_idx, column=0, padx=10, pady=5, sticky='w')
            
            cat = tk.Label(catFrame, text=impactName, width=label_column_width, anchor='w')
            cat.grid(row=row_idx, column=1, padx=10, pady=5, sticky='w')
            spacer = tk.Label(catFrame, text="", width=max_severity_length + 5)  # Spacer column
            spacer.grid(row=row_idx, column=2, padx=10, pady=5)

            cbVar = tk.IntVar()
            category_checkbuttons_row = []

            for j, (severity, weight) in enumerate(cbvalue):
                checkbox = tk.Checkbutton(catFrame, variable=cbVar, onvalue=weight, offvalue=0)
                checkbox.grid(row=row_idx, column=j+3, sticky='w')
                category_checkbuttons_row.append(checkbox)
            
            checkboxList.append((impactName, cbVar))
            category_checkbuttons.append(category_checkbuttons_row)
            
            subcat_label_row = []
            subcat_checkbutton_row = []

            # Create subcategory rows directly below the main category
            for k, subcatName in enumerate(subcategories):
                subcat_label = tk.Label(catFrame, text="    " + subcatName, width=label_column_width, anchor='w')
                subcat_label.grid(row=row_idx+1+k, column=1, padx=10, pady=5, sticky='w')
                subcat_label_row.append(subcat_label)
                subcatVar = tk.IntVar()
                
                subcat_checkbuttons_for_row = []
                for j, (severity, weight) in enumerate(cbvalue):
                    subcat_checkbox = tk.Checkbutton(catFrame, variable=subcatVar, onvalue=weight, offvalue=0)
                    subcat_checkbox.grid(row=row_idx+1+k, column=j+3, sticky='w')  # Adjusted column index
                    subcat_checkbuttons_for_row.append(subcat_checkbox)
                
                subcat_checkbutton_row.append(subcat_checkbuttons_for_row)
                checkboxList.append((subcatName, subcatVar))
                active_status[subcatName] = "Inactive"  # Initialize active status
            
            subcat_labels.append(subcat_label_row)
            subcat_checkbuttons.append(subcat_checkbutton_row)
            
            if subcategories:
                for label in subcat_label_row:
                    label.grid_remove()
                for checkbutton_row in subcat_checkbutton_row:
                    for checkbutton in checkbutton_row:
                        checkbutton.grid_remove()
            
            current_row += len(subcategories) + 1

    subcat_labels1, subcat_checkbuttons1, toggle_buttons1, category_checkbuttons1 = [], [], [], []
    subcat_labels2, subcat_checkbuttons2, toggle_buttons2, category_checkbuttons2 = [], [], [], []
    
    create_frame_widgets(frame1, subcat_labels1, subcat_checkbuttons1, toggle_buttons1, category_checkbuttons1, "Check an impact importance box for each category")
    create_frame_widgets(frame2, subcat_labels2, subcat_checkbuttons2, toggle_buttons2, category_checkbuttons2, "Check an impact extent box for each category")
