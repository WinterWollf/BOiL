from pathlib import Path
import os
import tkinter.font as tkFont
from ctypes import windll

OUTPUT_PATH = Path(__file__).parent
MAIN_ASSETS_PATH = OUTPUT_PATH / Path("assets/frame0")
CPM_ASSETS_PATH = OUTPUT_PATH / Path("assets/frame1")
FONTS_PATH = OUTPUT_PATH / Path("assets/fonts")

def relative_to_assets(path: str) -> Path:
    return MAIN_ASSETS_PATH / Path(path)

def relative_to_assets_2(path: str) -> Path:
    return CPM_ASSETS_PATH / Path(path)

def relative_to_fonts(path: str) -> Path:
    return FONTS_PATH / Path(path)

def load_custom_font(font_path: str, font_family: str, size: int) -> tkFont.Font:
    if os.name == 'nt':
        FR_PRIVATE = 0x10
        FR_NOT_ENUM = 0x20
        windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)

    available_fonts = list(tkFont.families())
    if font_family not in available_fonts:
        print(f"Font '{font_family}' ERROR.")
    else:
        print(f"Font '{font_family}' loaded successfully.")

    return tkFont.Font(family=font_family, size=size)