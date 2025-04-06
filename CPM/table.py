from tkinter import Toplevel, ttk, Label, Button
from tkinter import messagebox
from openpyxl import Workbook
from tkinter.filedialog import asksaveasfilename


def align_window(window):
    window_width = 800
    window_height = 600
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    window.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")


def save_to_excel(table_window, results):
    if not results or not results.activities:
        messagebox.showerror("Error", "No results available to save!")
        return

    file_path = asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        title="Save Results as Excel File"
    )
    if not file_path:
        return

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "CPM Results"

    headers = ["Activity", "ES", "EF", "LS", "LF", "Reserve"]
    sheet.append(headers)

    for name, activity in results.activities.items():
        sheet.append([name, activity.ES, activity.EF, activity.LS, activity.LF, activity.reserve])

    sheet.append([])
    sheet.append(["Critical Path", " -> ".join(results.critical_path)])

    try:
        workbook.save(file_path)
        messagebox.showinfo("Success", f"Results saved successfully to {file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {e}")

    table_window.destroy()


def create_results_table(parent_window, results):
    if not results or not results.activities:
        messagebox.showerror("Error", "No results available to display!")
        return

    table_window = Toplevel(parent_window)
    table_window.title("CPM Results Table")
    table_window.geometry("800x600")
    table_window.configure(bg="#4076FF")
    align_window(table_window)

    Label(
        table_window, text="CPM Results", font=("Arial", 16, "bold"), bg="#4076FF", fg="white"
    ).pack(pady=10)

    columns = ("Activity", "ES", "EF", "LS", "LF", "Reserve")
    tree = ttk.Treeview(table_window, columns=columns, show="headings", height=15)
    tree.pack(pady=10, padx=10, fill="both", expand=True)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=100)

    for name, activity in results.activities.items():
        tree.insert(
            "", "end", values=(name, activity.ES, activity.EF, activity.LS, activity.LF, activity.reserve)
        )

    critical_path_label = Label(
        table_window,
        text=f"Critical Path: {' -> '.join(results.critical_path)}",
        font=("Arial", 12, "bold"),
        bg="#4076FF",
        fg="white",
    )
    critical_path_label.pack(pady=10)

    Button(
        table_window,
        text="Save to Excel",
        command=lambda: save_to_excel(table_window, results),
        font=("Arial", 12),
        bg="white",
        fg="black",
    ).pack(pady=10)

    Button(
        table_window,
        text="Close",
        command=table_window.destroy,
        font=("Arial", 12),
        bg="white",
        fg="black",
    ).pack(pady=10)

    table_window.resizable(False, False)
