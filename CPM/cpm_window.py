from tkinter import Tk, Toplevel, Canvas, Entry, Text, Button, PhotoImage, Label
import tkinter.font as tkFont
from gui_paths import relative_to_fonts, relative_to_assets_2, load_custom_font
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from cpm import CPM
from table import create_results_table
from tkinter import filedialog
from activity import Activity, parseEventSequenceFormat, parsePredecessorformat, reverseEventSequenceFormat


def main_window(window):
    window.destroy()
    from main_window import create_main_gui
    create_main_gui()


def align_window(window):
    window_width = 1330
    window_height = 881
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    window.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")


def create_cpm_gui(cpm_window):
    align_window(cpm_window)

    font_path = str(relative_to_fonts("Kanit.ttf"))
    custom_font_3 = load_custom_font(font_path, "Kanit", 48*-1)
    custom_font_4 = load_custom_font(font_path, "Kanit", 20*-1)

    active_table = None

    canvas = Canvas(
        cpm_window,
        bg="#4076FF",
        height=881,
        width=1330,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas.place(x=0, y=0)
    canvas.create_rectangle(91.0, 794.0, 1054.0, 795.0, fill="#FFFFFF", outline="")
    canvas.create_rectangle(91.0, 105.0, 1255.0, 107.0, fill="#FFFFFF", outline="")

    canvas.create_text(378.0, 16.0, anchor="nw", text="Critical Path Method (CPM)", fill="#FFFFFF", font=custom_font_3)
    image_image_1 = PhotoImage(file=relative_to_assets_2("image_1.png"))
    canvas.create_image(1178.0, 795.0, image=image_image_1)

    canvas.create_text(92.0, 107.0, anchor="nw",
                       text="Choose the table and enter data into the fields below the table:", fill="#FFFFFF",
                       font=custom_font_4)
    

    def load_data_from_table1():
        activities = {}
        if not table1.get_children():
            messagebox.showwarning("Warning", "Table 1 is empty!")
            return {}
        for item in table1.get_children():
            values = table1.item(item, 'values')
            id_val, duration, events = values
            if not all([id_val, duration, events]):
                raise ValueError(f"Empty field detected in activity {id_val}")
            if not duration.isdigit():
                raise ValueError(f"Duration must be a number in activity {id_val}")
            event_parts = events.split('-')
            if len(event_parts) != 2:
                raise ValueError(
                    f"Events for activity {id_val} must be in 'start-end' format (e.g., '1-2') with numbers, not '{events}'")
            if not all(part.strip().isdigit() for part in event_parts):
                raise ValueError(
                    f"Events for activity {id_val} must contain numbers in 'start-end' format (e.g., '1-2'), not '{events}'")
            activities[id_val] = {
                'duration': int(duration),
                'events': events
            }
        return activities
    
    def load_data_from_table2():
        activities = {}
        if not table2.get_children():
            messagebox.showwarning("Warning", "Table 2 is empty!")
            return {}
        for item in table2.get_children():
            values = table2.item(item, 'values')
            id_val, duration, predecessors = values
            if not all([id_val, duration, predecessors]):
                raise ValueError(f"Empty field detected in activity {id_val}")
            if not duration.isdigit():
                raise ValueError(f"Duration must be a number in activity {id_val}")
            pred_list = predecessors.split(',') if predecessors != '-' else []
            activities[id_val] = {
                'duration': int(duration),
                'predecessors': pred_list
            }

        return activities
    

    def create_cpm_from_tables():
        if active_table == "table1":
                loaded_data = load_data_from_table1()
                if len(loaded_data) == 0:
                    return False
                activities = parseEventSequenceFormat(loaded_data)
        else:  # table2
            loaded_data = load_data_from_table2()
            if len(loaded_data) == 0:
                return False  
            activities = parsePredecessorformat(loaded_data)

        cpm = CPM(activities)
        cpm.calculate()
        cpm.critical_path = cpm.criticalPath()

        global results
        results = cpm


    def calculate_cpm():
        nonlocal active_table
        if not active_table:
            messagebox.showwarning("Warning", "Please enter data into one of the tables first!")
            return False
        
        try:
            create_cpm_from_tables()

            global results

            result_text = "CPM Results:\n"
            for name, act in results.activities.items():
                result_text += (f"Activity {name}: ES={act.ES}, EF={act.EF}, "
                                f"LS={act.LS}, LF={act.LF}, Reserve={act.reserve}\n")
            result_text += "\nCritical Path: " + " -> ".join(results.critical_path)
            messagebox.showinfo("CPM Results", result_text)
            return True

        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return False
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            return False

    def draw_aon():
        if calculate_cpm() and 'results' in globals():
            results.drawAON()

    def draw_aoa():
        if calculate_cpm() and 'results' in globals():
            results.drawAOA()

    def draw_gantt():
        if calculate_cpm() and 'results' in globals():
            results.drawGantt()

    def draw_table():
        if calculate_cpm() and 'results' in globals():
            create_results_table(cpm_window, results)

    def add_to_table1():
        nonlocal active_table
        if active_table == "table2":
            messagebox.showwarning("Warning", "Cannot add to Table 1: Table 2 is already in use!")
            return
        id_data = entry_id1.get()
        duration_data = entry_duration1.get()
        events_data = entry_events1.get()
        if id_data and duration_data and events_data:
            table1.insert("", "end", values=(id_data, duration_data, events_data))
            entry_id1.delete(0, "end")
            entry_duration1.delete(0, "end")
            entry_events1.delete(0, "end")
            active_table = "table1"
            entry_id2.config(state="disabled")
            entry_duration2.config(state="disabled")
            entry_predecessors2.config(state="disabled")
            button_add2.config(state="disabled")

    def add_to_table2():
        nonlocal active_table
        if active_table == "table1":
            messagebox.showwarning("Warning", "Cannot add to Table 2: Table 1 is already in use!")
            return
        id_data = entry_id2.get()
        duration_data = entry_duration2.get()
        predecessors_data = entry_predecessors2.get()
        if id_data and duration_data and predecessors_data:
            table2.insert("", "end", values=(id_data, duration_data, predecessors_data))
            entry_id2.delete(0, "end")
            entry_duration2.delete(0, "end")
            entry_predecessors2.delete(0, "end")
            active_table = "table2"
            entry_id1.config(state="disabled")
            entry_duration1.config(state="disabled")
            entry_events1.config(state="disabled")
            button_add1.config(state="disabled")

    def remove_from_table1():
        selected_item = table1.selection()
        if selected_item:
            table1.delete(selected_item)
            if not table1.get_children():
                nonlocal active_table
                active_table = None
                entry_id2.config(state="normal")
                entry_duration2.config(state="normal")
                entry_predecessors2.config(state="normal")
                button_add2.config(state="normal")

    def remove_from_table2():
        selected_item = table2.selection()
        if selected_item:
            table2.delete(selected_item)
            if not table2.get_children():
                nonlocal active_table
                active_table = None
                entry_id1.config(state="normal")
                entry_duration1.config(state="normal")
                entry_events1.config(state="normal")
                button_add1.config(state="normal")

    def export_data():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv", 
            filetypes=[("Csv files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            create_cpm_from_tables()

            global results

            results.save_to_csv(file_path)

    def ask_load_as_predecessor():
        dialog = Toplevel()
        dialog.title("Choose format")
        dialog.geometry("300x150")

        # Center the dialog on the screen
        dialog.update_idletasks()
        root_x = cpm_window.winfo_screenwidth() // 2 - 150
        root_y = cpm_window.winfo_screenheight() // 2 - 75
        dialog.geometry(f"300x150+{root_x}+{root_y}")
        
        Label(dialog, text="What format to load the data in?").pack(pady=10)

        use_predecessor = True
        
        def on_event():
            nonlocal use_predecessor
            use_predecessor = False
            dialog.destroy()
        
        def on_pred():
            nonlocal use_predecessor
            use_predecessor = True
            dialog.destroy()
        
        Button(dialog, text="Event Sequence", command=on_event).pack(side="left", padx=20, pady=10)
        Button(dialog, text="Predecessor", command=on_pred).pack(side="right", padx=20, pady=10)
        
        dialog.transient(cpm_window)
        dialog.grab_set()
        cpm_window.wait_window(dialog)

        return use_predecessor

    def clear_tables():
        # clear tables
        nonlocal active_table
        active_table = ""
        for c in table1.get_children():
            table1.delete(c)
        for c in table2.get_children():
            table2.delete(c)

    def import_data():
        global results
        results = CPM()

        file_path = filedialog.askopenfilename(
            defaultextension=".csv", 
            filetypes=[("Csv files", "*.csv"), ("All files", "*.*")]
        )

        results.read_from_csv(file_path)

        use_predecessor = ask_load_as_predecessor()

        clear_tables()

        nonlocal active_table

        if use_predecessor:
            # load into table2
            active_table = "table2"
            for activity in results.activities.values():
                pred = ",".join(activity.predecessors) if len(activity.predecessors) > 0 else "-"
                table2.insert("", "end", values=(activity.name, activity.duration, pred))
        else:
            active_table = "table1"
            data = reverseEventSequenceFormat(results.activities)
            for name, data in data.items():
                table1.insert("", "end", values=(name, data["duration"], data["events"]))

    

    button_image_1 = PhotoImage(file=relative_to_assets_2("button_1.png"))
    button_1 = Button(
        cpm_window, image=button_image_1, borderwidth=0, highlightthickness=0,
        command=draw_aon,
        relief="flat"
    )
    button_1.place(x=998.0, y=249.0, width=204.0, height=57.0)

    button_image_2 = PhotoImage(file=relative_to_assets_2("button_2.png"))
    button_2 = Button(
        cpm_window, image=button_image_2, borderwidth=0, highlightthickness=0,
        command=draw_aoa,
        relief="flat"
    )
    button_2.place(x=998.0, y=330.0, width=204.0, height=57.0)

    button_image_3 = PhotoImage(file=relative_to_assets_2("button_3.png"))
    button_3 = Button(
        cpm_window, image=button_image_3, borderwidth=0, highlightthickness=0,
        command=draw_gantt,
        relief="flat"
    )
    button_3.place(x=998.0, y=411.0, width=204.0, height=57.0)

    button_image_7 = PhotoImage(file=relative_to_assets_2("spreadsheet.png"))
    button_7 = Button(
        cpm_window, image=button_image_7, borderwidth=0, highlightthickness=0,
        command=draw_table,
        relief="flat"
    )
    button_7.place(x=998.0, y=485.0, width=204.0, height=57.0)

    canvas.create_text(957.0, 557.0, anchor="nw", text="Import or export data (CSV file)", fill="#FFFFFF",
                       font=custom_font_4)

    button_image_4 = PhotoImage(file=relative_to_assets_2("button_4.png"))
    button_4 = Button(cpm_window, image=button_image_4, borderwidth=0, highlightthickness=0,
                      command=lambda: import_data(), relief="flat")
    button_4.place(x=959.0, y=601.0, width=141.0, height=48.0)

    button_image_5 = PhotoImage(file=relative_to_assets_2("button_5.png"))
    button_5 = Button(cpm_window, image=button_image_5, borderwidth=0, highlightthickness=0,
                      command=lambda: export_data(), relief="flat")
    button_5.place(x=1105.0, y=601.0, width=138.0, height=48.0)

    button_image_6 = PhotoImage(file=relative_to_assets_2("button_6.png"))
    button_6 = Button(cpm_window, image=button_image_6, borderwidth=0, highlightthickness=0,
                      command=lambda: main_window(cpm_window), relief="flat")
    button_6.place(x=99.0, y=29.0, width=50.0, height=50.0)

    table1 = ttk.Treeview(cpm_window, columns=("A", "B", "C"), show="headings")
    table1.heading("A", text="ID")
    table1.heading("B", text="Duration")
    table1.heading("C", text="Events (Start-End)")
    table1.column("A", width=50, anchor="center")
    table1.column("B", width=100, anchor="center")
    table1.column("C", width=150, anchor="center")
    table1.place(x=92, y=160, width=350, height=550)

    table2 = ttk.Treeview(cpm_window, columns=("D", "E", "F"), show="headings")
    table2.heading("D", text="ID")
    table2.heading("E", text="Duration")
    table2.heading("F", text="Predecessors (use '-' if none)")
    table2.column("D", width=50, anchor="center")
    table2.column("E", width=100, anchor="center")
    table2.column("F", width=180, anchor="center")
    table2.place(x=500, y=160, width=350, height=550)

    entry_id1 = Entry(cpm_window, font=custom_font_4)
    entry_duration1 = Entry(cpm_window, font=custom_font_4)
    entry_events1 = Entry(cpm_window, font=custom_font_4)
    entry_id1.place(x=92, y=730, width=50)
    entry_duration1.place(x=150, y=730, width=50)
    entry_events1.place(x=208, y=730, width=90)

    entry_id2 = Entry(cpm_window, font=custom_font_4)
    entry_duration2 = Entry(cpm_window, font=custom_font_4)
    entry_predecessors2 = Entry(cpm_window, font=custom_font_4)
    entry_id2.place(x=500, y=730, width=50)
    entry_duration2.place(x=558, y=730, width=50)
    entry_predecessors2.place(x=616, y=730, width=90)

    button_add1 = Button(cpm_window, text="ADD", command=add_to_table1, font=custom_font_4)
    button_add1.place(x=314, y=729, width=70, height=40)

    button_add2 = Button(cpm_window, text="ADD", command=add_to_table2, font=custom_font_4)
    button_add2.place(x=722, y=729, width=70, height=40)

    trash_image = Image.open(relative_to_assets_2("trash.png"))
    trash_image = trash_image.resize((30, 30), Image.Resampling.LANCZOS)
    trash_icon = ImageTk.PhotoImage(trash_image)
    cpm_window.trash_icon = trash_icon

    button_remove1 = Button(cpm_window, image=trash_icon, command=remove_from_table1, borderwidth=0)
    button_remove1.place(x=390, y=729, width=38, height=38)

    button_remove2 = Button(cpm_window, image=trash_icon, command=remove_from_table2, borderwidth=0)
    button_remove2.place(x=798, y=729, width=38, height=38)

    cpm_window.resizable(False, False)
    cpm_window.mainloop()
