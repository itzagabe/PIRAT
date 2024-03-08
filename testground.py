import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Centered Buttons")
    root.geometry("400x200")

    frame = tk.Frame(root)
    frame.pack(expand=True, fill=tk.BOTH)

    button1 = tk.Button(frame, text="Button 1")
    button2 = tk.Button(frame, text="Button 2")

    # Centering buttons horizontally using pack
    button1.pack(side=tk.LEFT, padx=10, pady=10)
    button2.pack(side=tk.LEFT, padx=10, pady=10)

    # Add an empty label to push buttons to the center
    empty_label = tk.Label(frame, text="")
    empty_label.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
