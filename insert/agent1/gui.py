import tkinter as tk
from tkinter import ttk, messagebox
from automator import fill_patient_form # Import our robot function

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Patient Entry Form")
        self.root.geometry("400x280")
        
        style = ttk.Style(root)
        style.theme_use("clam")

        form_frame = ttk.Frame(root, padding="20")
        form_frame.pack(fill="both", expand=True)

        labels = ["ID", "Name", "Address", "Date of Birth", "Age", "Sex"]
        self.entries = {}
        for i, label_text in enumerate(labels):
            label = ttk.Label(form_frame, text=f"{label_text}:")
            label.grid(row=i, column=0, sticky="w", pady=5, padx=5)

            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, sticky="ew", pady=5, padx=5)
            # Use a simple key for the dictionary (e.g., "id", "name")
            self.entries[label_text.lower().replace(" ", "_").split('(')[0].strip()] = entry

        add_button = ttk.Button(form_frame, text="Add Patient to Legacy System", command=self.submit_data)
        add_button.grid(row=len(labels), column=0, columnspan=2, pady=15)

        form_frame.columnconfigure(1, weight=1)
        self.root.mainloop()

    def submit_data(self):
        patient_data = {key: entry.get() for key, entry in self.entries.items()}
        
        # Basic validation
        if not patient_data.get("id") or not patient_data.get("name"):
            messagebox.showerror("Error", "Patient ID and Name are required.")
            return

        try:
            print("GUI is calling the automator...")
            fill_patient_form(patient_data)
            messagebox.showinfo("Success", "Patient data submitted to the legacy system successfully!")
            # Optionally clear fields after submission
            for entry in self.entries.values():
                entry.delete(0, tk.END)
                
        except Exception as e:
            messagebox.showerror("Automation Failed", f"An error occurred: {e}")