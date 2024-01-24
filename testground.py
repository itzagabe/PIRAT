import tkinter as tk

def select_item(array):
    def on_button_click():
        selected_index = listbox.curselection()
        if selected_index:
            selected_value = array[selected_index[0]]
            print(f"Selected value: {selected_value}")
            root.destroy()  # Close the Tkinter window

    root = tk.Tk()
    root.title("Array Selection")

    listbox = tk.Listbox(root)
    for item in array:
        listbox.insert(tk.END, item)
    listbox.pack(pady=10)

    button = tk.Button(root, text="Select", command=on_button_click)
    button.pack(pady=10)

    root.mainloop()

# Example usage:
my_array = ["Item 1", "Item 2", "Item 3", "Item 4"]
select_item(my_array)
