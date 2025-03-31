from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import tkinter.font as tkFont
from gui_paths import relative_to_assets, relative_to_fonts


def align_window(window):
    window_width = 1024
    window_height = 768

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)

    window.geometry(f"{window_width}x{window_height}+{int(x_coordinate)}+{int(y_coordinate)}")


def window_changer(window):
    window.destroy()

    new_window = Tk()
    new_window.title("Critical Path Method (CPM)")
    new_window.geometry("1330x881")
    new_window.configure(bg="#4076FF")

    from cpm_window import create_cpm_gui
    create_cpm_gui(new_window)


def create_main_gui():
    window = Tk()

    window.title("Main menu")
    window.geometry("1024x768")
    window.configure(bg = "#4076FF")
    align_window(window)


    font_path = str(relative_to_fonts("Kanit.ttf"))
    custom_font_1 = tkFont.Font(family="Kanit", size=36 * -1)
    custom_font_2 = tkFont.Font(family="Kanit", size=64 * -1)


    canvas = Canvas(
        window,
        bg = "#4076FF",
        height = 768,
        width = 1024,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    canvas.place(x = 0, y = 0)
    canvas.create_text(
        76.0,
        456.0,
        anchor="nw",
        text="Broker problem:",
        fill="#FFFFFF",
        font=custom_font_1
    )

    canvas.create_text(
        76.0,
        284.0,
        anchor="nw",
        text="Critical Path Method (CPM):",
        fill="#FFFFFF",
        font=custom_font_1
    )

    canvas.create_rectangle(
        75.0,
        700.0,
        937.9999841448043,
        701.9965318025808,
        fill="#FFFFFF",
        outline="")

    canvas.create_rectangle(
        75.0,
        178.0,
        937.9999841448043,
        179.9965318025807,
        fill="#FFFFFF",
        outline="")

    canvas.create_text(
        76.0,
        29.0,
        anchor="nw",
        text="Welcome!",
        fill="#FFFFFF",
        font=custom_font_2
    )

    canvas.create_text(
        76.0,
        112.0,
        anchor="nw",
        text="Choose one of the methods:",
        fill="#FFFFFF",
        font=custom_font_1
    )

    button_image_1 = PhotoImage(
        file=relative_to_assets("button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: window_changer(window),
        relief="flat"
    )
    button_1.place(
        x=76.0,
        y=339.0,
        width=196.0,
        height=72.0
    )

    button_image_2 = PhotoImage(
        file=relative_to_assets("button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_2 clicked"),
        relief="flat"
    )
    button_2.place(
        x=76.0,
        y=511.0,
        width=196.0,
        height=72.0
    )

    image_image_1 = PhotoImage(
        file=relative_to_assets("image_1.png"))
    image_1 = canvas.create_image(
        858.0,
        98.0,
        image=image_image_1
    )

    window.resizable(False, False)
    window.mainloop()
