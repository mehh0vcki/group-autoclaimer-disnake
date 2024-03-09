import os
from rgbprint import gradient_print
from pyfiglet import Figlet


def get_terminal_width() -> int:
    try:
        return os.get_terminal_size().columns
    except:
        return 80  # default width


def middle_text(text: str, width: int) -> str:
    padding: int = (width - len(text)) // 2
    return " " * padding + text


def generate_logo() -> None:
    width: int = get_terminal_width()
    figlet = Figlet("elite", width=width)
    art: str = figlet.renderText("mehhovcki")
    center: str = "\n".join(middle_text(line, width) for line in art.splitlines())
    gradient_print(center, start_color="#fa5796", end_color="#99254f")


def gradient_print_text(
    text: str, width: int, retarted: bool, start_color: str, end_color: str
) -> None:
    if retarted:
        gradient_print(
            middle_text(text, width),
            start_color=start_color,
            end_color=end_color,
            end="\r",
        )
    else:
        gradient_print(
            middle_text(text, width), start_color=start_color, end_color=end_color
        )


def generate_text(text: str, importance: int) -> None:
    width: int = get_terminal_width()
    if importance == 0:
        gradient_print_text(text, width, False, "#fa5796", "#99254f")
    elif importance == 1:
        gradient_print_text(text, width, False, "#904bb8", "#7f1796")
    elif importance == 2:
        gradient_print_text(text, width, False, "#67cfa9", "#159640")
    elif importance == 3:
        gradient_print_text(text, width, True, "#fa5796", "#99254f")
