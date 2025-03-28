from pathlib import Path

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