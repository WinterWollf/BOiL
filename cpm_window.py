from tkinter import Toplevel, Canvas, Entry, Text, Button, PhotoImage
import tkinter.font as tkFont
from gui_paths import relative_to_fonts, relative_to_assets_2
from tkinter import ttk
from PIL import Image, ImageTk

def create_cpm_gui(parent_window):

    cpm_window = Toplevel(parent_window)
    cpm_window.geometry("1330x881")
    cpm_window.configure(bg = "#4076FF")

    font_path = str(relative_to_fonts("Kanit.ttf"))
    custom_font_1 = tkFont.Font(family="Kanit", size=36 * -1)
    custom_font_2 = tkFont.Font(family="Kanit", size=64 * -1)
    custom_font_3 = tkFont.Font(family="Kanit", size=48 * -1)
    custom_font_4 = tkFont.Font(family="Kanit", size=20 * -1)

    canvas = Canvas(
        cpm_window,
        bg = "#4076FF",
        height = 881,
        width = 1330,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    canvas.place(x = 0, y = 0)
    canvas.create_rectangle(
        91.0,
        794.0,
        1054.0,
        795.0,
        fill="#FFFFFF",
        outline="")

    canvas.create_rectangle(
        91.0,
        105.0000000596817,
        1254.9999502895953,
        107.0,
        fill="#FFFFFF",
        outline="")

    canvas.create_text(
        378.0,
        16.0,
        anchor="nw",
        text="Critical Path Method (CPM)",
        fill="#FFFFFF",
        font=custom_font_3
    )

    image_image_1 = PhotoImage(
        file=relative_to_assets_2("image_1.png"))
    image_1 = canvas.create_image(
        1178.0,
        795.0,
        image=image_image_1
    )

    canvas.create_text(
        92.0,
        107.0,
        anchor="nw",
        text="Enter data into the selected table in the fields below the table:",
        fill="#FFFFFF",
        font=custom_font_4
    )

    button_image_1 = PhotoImage(
        file=relative_to_assets_2("button_1.png"))
    button_1 = Button(
        cpm_window,
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_1 clicked"),
        relief="flat"
    )
    button_1.place(
        x=998.0,
        y=249.0,
        width=204.0,
        height=57.0
    )

    button_image_2 = PhotoImage(
        file=relative_to_assets_2("button_2.png"))
    button_2 = Button(
        cpm_window,
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_2 clicked"),
        relief="flat"
    )
    button_2.place(
        x=998.0,
        y=330.0,
        width=204.0,
        height=57.0
    )

    button_image_3 = PhotoImage(
        file=relative_to_assets_2("button_3.png"))
    button_3 = Button(
        cpm_window,
        image=button_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_3 clicked"),
        relief="flat"
    )
    button_3.place(
        x=998.0,
        y=411.0,
        width=204.0,
        height=57.0
    )

    canvas.create_text(
        957.0,
        557.0,
        anchor="nw",
        text="Import or export data (CSV file)",
        fill="#FFFFFF",
        font=custom_font_4
    )

    button_image_4 = PhotoImage(
        file=relative_to_assets_2("button_4.png"))
    button_4 = Button(
        cpm_window,
        image=button_image_4,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_4 clicked"),
        relief="flat"
    )
    button_4.place(
        x=959.0,
        y=601.0,
        width=141.0,
        height=48.0
    )

    button_image_5 = PhotoImage(
        file=relative_to_assets_2("button_5.png"))
    button_5 = Button(
        cpm_window,
        image=button_image_5,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_5 clicked"),
        relief="flat"
    )
    button_5.place(
        x=1105.0,
        y=601.0,
        width=138.0,
        height=48.0
    )

    button_image_6 = PhotoImage(
        file=relative_to_assets_2("button_6.png"))
    button_6 = Button(
        cpm_window,
        image=button_image_6,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: cpm_window.destroy(),
        relief="flat"
    )
    button_6.place(
        x=99.0,
        y=29.0,
        width=50.0,
        height=50.0
    )


    def add_to_table1():
        id_data = entry_id1.get()
        duration_data = entry_duration1.get()
        events_data = entry_events1.get()
        if id_data and duration_data and events_data:
            table1.insert("", "end", values=(id_data, duration_data, events_data))
            entry_id1.delete(0, "end")
            entry_duration1.delete(0, "end")
            entry_events1.delete(0, "end")

    def add_to_table2():
        id_data = entry_id2.get()
        duration_data = entry_duration2.get()
        predecessors_data = entry_predecessors2.get()
        if id_data and duration_data and predecessors_data:
            table2.insert("", "end", values=(id_data, duration_data, predecessors_data))
            entry_id2.delete(0, "end")
            entry_duration2.delete(0, "end")
            entry_predecessors2.delete(0, "end")

    def remove_from_table1():
        selected_item = table1.selection()
        if selected_item:
            table1.delete(selected_item)

    def remove_from_table2():
        selected_item = table2.selection()
        if selected_item:
            table2.delete(selected_item)



    # Table 1
    table1 = ttk.Treeview(cpm_window, columns=("A", "B", "C"), show="headings")
    table1.heading("A", text="ID")
    table1.heading("B", text="Duration")
    table1.heading("C", text="Events (Start-End)")
    table1.column("A", width=50, anchor="center")
    table1.column("B", width=100, anchor="center")
    table1.column("C", width=150, anchor="center")
    table1.place(x=92, y=160, width=350, height=550)

    # Table 2
    table2 = ttk.Treeview(cpm_window, columns=("D", "E", "F"), show="headings")
    table2.heading("D", text="ID")
    table2.heading("E", text="Duration")
    table2.heading("F", text="Predecessors (use '-' if none)")
    table2.column("D", width=50, anchor="center")
    table2.column("E", width=100, anchor="center")
    table2.column("F", width=180, anchor="center")
    table2.place(x=500, y=160, width=350, height=550)

    # Fields for data
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


    # Buttons to add data to tables
    button_add1 = Button(cpm_window, text="ADD", command=add_to_table1, font=custom_font_4)
    button_add1.place(x=314, y=729, width=70, height=40)

    button_add2 = Button(cpm_window, text="ADD", command=add_to_table2, font=custom_font_4)
    button_add2.place(x=722, y=729, width=70, height=40)


    trash_image = Image.open(relative_to_assets_2("trash.png"))
    trash_image = trash_image.resize((30, 30), Image.Resampling.LANCZOS)
    trash_icon = ImageTk.PhotoImage(trash_image)
    cpm_window.trash_icon = trash_icon


    # Buttons to remove data from tables
    button_remove1 = Button(cpm_window, image=trash_icon, command=remove_from_table1, borderwidth=0)
    button_remove1.place(x=390, y=729, width=38, height=38)

    button_remove2 = Button(cpm_window, image=trash_icon, command=remove_from_table2, borderwidth=0)
    button_remove2.place(x=798, y=729, width=38, height=38)


    cpm_window.resizable(False, False)
    cpm_window.mainloop()