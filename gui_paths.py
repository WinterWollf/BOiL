from pathlib import Path

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("assets/frame0")
FONTS_PATH = OUTPUT_PATH / Path("assets/fonts")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

def relative_to_fonts(path: str) -> Path:
    return FONTS_PATH / Path(path)