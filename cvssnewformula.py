import tkinter as tk
from tkinter import ttk
import math

baseScore = 0
temporalScore = 0

def CalculateBaseScore():
    global baseScore
    def CustomRoundUp(number):
        return math.ceil(number * 10) / 10

    exploitability = 0
    baseScore = 0

    scopeChanged = False
    selected_values = [numeric_mapping[var.get()] for var in base_score_dropdown_vars]

    if selected_values[4]:
        scopeChanged = True
    
    if scopeChanged:
        if selected_values[2] == 0.62: # 0.62 (0.68 if Scope / Modified Scope is Changed)
            selected_values[2] = 0.68
        elif selected_values[2] == 0.27: # 0.27 (0.50 if Scope / Modified Scope is Changed)
            selected_values[2] = 0.5

    exploitability = 8.22 * selected_values[0] * selected_values[1] * selected_values[2] * selected_values[3]

    if scopeChanged:
        baseScore = CustomRoundUp(min(exploitability, 10))
    else:
        baseScore = CustomRoundUp(min(1.08 * exploitability, 10))

    # Update the base score label
    base_score_label.config(text=f"Base score: {baseScore}", fg=calculate_gradient_color(baseScore))
    calculate_cvss_score()
    
def CalculateTemporalScore():
    global temporalScore
    def CustomRoundUp(number):
        return math.ceil(number * 100) / 100

    exploitability = 0
    temporalScore = 0

    selected_values = [numeric_mapping[var.get()] for var in temporal_score_dropdown_vars]

    temporalScore = selected_values[0] * selected_values[1] * selected_values[2]
    temporalScore = CustomRoundUp(temporalScore)

    # Update the base score label
    temporal_score_label.config(text=f"Temporal score: {temporalScore}")
    calculate_cvss_score()

def calculate_cvss_score():
    global baseScore, temporalScore
    cvss_score = baseScore * temporalScore
    # Update the CVSS score label
    cvss_score_label.config(text=f"CVSS Score: {math.ceil(cvss_score * 100) / 100}", fg=calculate_gradient_color(baseScore))
    
def calculate_gradient_color(base_score):
    # Calculate the RGB values for the gradient color based on the base score
    green = min(max(int((1 - base_score / 3.2) * 180), 0), 255)
    red = min(max(int((base_score / 3.2) * 255), 0), 255)
    # Convert RGB values to hexadecimal color code
    color = f'#{red:02x}{green:02x}00'
    return color



    # Calculation logic for temporal score goes here
    # You can reuse the logic from CalculateBaseScore() and make necessary modifications for temporal score

def on_base_score_dropdown_change(*args):
    CalculateBaseScore()

def on_temporal_score_dropdown_change(*args):
    CalculateTemporalScore()

root = tk.Tk()
root.title("Dropdown Calculator")

# Define unique options for each dropdown along with their names
base_options_and_names = [
    ({"Network": 0.85, "Adjacent Network": 0.62, "Local": 0.55, "Physical" : 0.2}, "Attack Vector"),
    ({"Low": 0.77, "High": 0.44}, "Attack Complexity"),
    ({"None": 0.85, "Low": 0.62, "High": 0.27}, "Privileges Required"),
    ({"None": 0.85, "Required": 0.62}, "User Interaction"),
    ({"Unchanged": 0, "Changed": 1}, "Scope")
]

temporal_options_and_names = [
    ({"Not Defined": 1, "High": 1, "Functional": 0.97, "Proof of Concept" : 0.94, "Unproven": 0.91}, "Exploit Code Maturity"),
    ({"Not Defined": 1, "Unavailable": 1, "Workaround" : 0.97, "Temporary Fix" : 0.96, "Official Fix" : 0.95}, "Attack Complexity"),
    ({"Not Defined": 1, "Confirmed": 1, "Reasonable": 0.96, "Unknown" : 0.92}, "Report Confidence"),
]

base_score_dropdown_vars = []
temporal_score_dropdown_vars = []
numeric_mapping = {}

# Create and place dropdowns for base score
for i, (options, name) in enumerate(base_options_and_names):
    label = tk.Label(root, text=f"{name}:")
    label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
    var = tk.StringVar(root)
    default_option = list(options.keys())[0]
    var.set(default_option)  # Set default value
    dropdown = ttk.Combobox(root, textvariable=var, values=list(options.keys()), state="readonly")
    dropdown.grid(row=i, column=1, padx=10, pady=5)
    base_score_dropdown_vars.append(var)
    numeric_mapping.update(options)
    var.trace_add("write", on_base_score_dropdown_change)  # Call on_base_score_dropdown_change function when the dropdown value changes

# Create and place dropdowns for temporal score
for i, (options, name) in enumerate(temporal_options_and_names):
    label = tk.Label(root, text=f"{name}:")
    label.grid(row=i, column=2, padx=10, pady=5, sticky="w")
    var = tk.StringVar(root)
    default_option = list(options.keys())[0]
    var.set(default_option)  # Set default value
    dropdown = ttk.Combobox(root, textvariable=var, values=list(options.keys()), state="readonly")
    dropdown.grid(row=i, column=3, padx=10, pady=5)
    temporal_score_dropdown_vars.append(var)
    numeric_mapping.update(options)
    var.trace_add("write", on_temporal_score_dropdown_change)  # Call on_temporal_score_dropdown_change function when the dropdown value changes

# Create and place label for displaying base score
base_score_label = tk.Label(root)
base_score_label.grid(row=len(base_options_and_names), column=0, columnspan=2, pady=10)

# Create and place label for displaying temporal score
temporal_score_label = tk.Label(root)
temporal_score_label.grid(row=len(base_options_and_names), column=2, columnspan=2, pady=10)

# Create and place label for displaying CVSS score
cvss_score_label = tk.Label(root)
cvss_score_label.grid(row=len(base_options_and_names) + 1, column=0, columnspan=4, pady=10)

root.resizable(False, False)
CalculateBaseScore()
CalculateTemporalScore()

root.mainloop()
