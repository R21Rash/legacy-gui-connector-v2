import tkinter as tk
from tkinter import ttk, messagebox
from automator import fill_patient_form # Import our robot function
import os

COUNTER_PATH = os.path.join(os.path.dirname(__file__), "id_counter.txt")

def _load_counter(default_value: int = 25) -> int:
    try:
        with open(COUNTER_PATH, "r", encoding="utf-8") as f:
            v = int((f.read() or "").strip())
            return v if v > 0 else default_value
    except Exception:
        return default_value

def _save_counter(v: int) -> None:
    try:
        with open(COUNTER_PATH, "w", encoding="utf-8") as f:
            f.write(str(int(v)))
    except Exception:
        pass

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

        # Default ID from persisted counter (starts at 25)
        try:
            current_id = _load_counter(25)
            self.entries["id"].delete(0, tk.END)
            self.entries["id"].insert(0, str(current_id))
        except Exception:
            pass

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
            # Increment and prefill next ID (25 → 26 → ...)
            try:
                base = _load_counter(25)
                # If user typed a numeric id, use that as base
                try:
                    base = int(patient_data.get("id") or base)
                except Exception:
                    pass
                nxt = base + 1
                _save_counter(nxt)
                self.entries["id"].insert(0, str(nxt))
            except Exception:
                pass
                
        except Exception as e:
            messagebox.showerror("Automation Failed", f"An error occurred: {e}")