import tkinter as tk

selected_values = {
    "Exploit Code Maturity": 'E:X',
    "Remediation Level": 'RL:X',
    "Report Confidence": 'RC:X'
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

def create_popup(root, selected_values):
    global popup
    popup = tk.Toplevel(root)
    popup.title("Dropdown Selection")

    dropdown_options = {
        "Exploit Code Maturity": ["Not Defined", "Unproven that exploit exists", "Proof of concept code", "Functional exploit exists", "High"],
        "Remediation Level": ["Not Defined", "Official Fix", "Temporary Fix", "Workaround", "Unavailable"],
        "Report Confidence": ["Not Defined", "Unknown", "Reasonable", "Confirmed"]
    }

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
    popup.wait_window()

def get_E_RL_RC(root):
    create_popup(root, selected_values)
    E = 'E:' + str(selected_values['Exploit Code Maturity'])
    RL = 'RL:' + str(selected_values['Remediation Level']) 
    RC = "RC:" + str(selected_values['Report Confidence']) 
    return E, RL, RC

if __name__ == "__main__":
    # Main logic
    root = tk.Tk()
    root.title("Main Window")

    open_popup_button = tk.Button(root, text="Open Popup", command=get_E_RL_RC)
    open_popup_button.pack(pady=10)

    root.mainloop()
