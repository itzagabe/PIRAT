import tkinter as tk

selected_values = {
    "Exploit Code Maturity": 'X',
    "Remediation Level": 'X',
    "Report Confidence": 'X'
}

def map_selected_option(selected_dropdown, selected_option):
    global selected_values
    mappings = {
        "Exploit Code Maturity": {
            "Not Defined": "X",
            "Unproven that exploit exists": "U",
            "Proof of concept code": "P",
            "Functional exploit exists": "F",
            "High": "H"
        },
        "Remediation Level": {
            "Not Defined": "X",
            "Official Fix": "O",
            "Temporary Fix": "T",
            "Workaround": "W",
            "Unavailable": "U"
        },
        "Report Confidence": {
            "Not Defined": "X",
            "Unknown": "U",
            "Reasonable": "R",
            "Confirmed": "C"
        }
    }
    selected_values[selected_dropdown] = mappings[selected_dropdown].get(selected_option)

def select_and_close_window():
    popup.destroy()  # Close the popup window when the "Select" button is clicked

def create_popup(name):
    global popup
    popup = tk.Toplevel()
    popup.title(name)

    dropdown_options = {
        "Exploit Code Maturity": ["Not Defined", "Unproven that exploit exists", "Proof of concept code", "Functional exploit exists", "High"],
        "Remediation Level": ["Not Defined", "Official Fix", "Temporary Fix", "Workaround", "Unavailable"],
        "Report Confidence": ["Not Defined", "Unknown", "Reasonable", "Confirmed"]
    }

    close_flag = True  # Flag to indicate how the window was closed

    def on_close():
        nonlocal close_flag
        close_flag = False
        select_and_close_window()

    for dropdown_name, options in dropdown_options.items():
        label = tk.Label(popup, text=f"{dropdown_name}:")
        label.pack(padx=10, pady=5, anchor='w')

        selected_option = tk.StringVar(popup)
        selected_option.set(options[0])

        option_menu = tk.OptionMenu(popup, selected_option, *options,
                                    command=lambda selected_option, name=dropdown_name: map_selected_option(name, selected_option))
        option_menu.config(width=25)
        option_menu.pack(padx=10, pady=5, anchor='w')

    select_button = tk.Button(popup, text="Select", command=select_and_close_window)
    select_button.pack(pady=10)

    popup.geometry('+%d+%d'%(200,300))
    popup.protocol("WM_DELETE_WINDOW", on_close)
    popup.wait_window()

    return close_flag

def GetModifiedCVSS(name):
    closeFlag = create_popup(name)
    E = 'E:' + str(selected_values['Exploit Code Maturity'])
    RL = 'RL:' + str(selected_values['Remediation Level']) 
    RC = "RC:" + str(selected_values['Report Confidence']) 
    return (E, RL, RC), closeFlag

if __name__ == "__main__":
    # Main logic
    root = tk.Tk()
    root.title("Main Window")

    open_popup_button = tk.Button(root, text="Open Popup", command=GetModifiedCVSS)
    open_popup_button.pack(pady=10)

    root.mainloop()

