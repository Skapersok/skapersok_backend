import os
import sys

import art

import auth
import constants
from dbsetup import some_database
from settings import settings


def _supports_color():
    """Check if the terminal supports ANSI color codes."""

    if os.environ.get("NO_COLOR") is not None:
        return False

    if os.environ.get("FORCE_COLOR") is not None:
        return True

    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False

    if os.name == "nt":
        # Windows 10+ terminals support ANSI; older cmd.exe doesn't
        return "ANSICON" in os.environ or "WT_SESSION" in os.environ or "TERM" in os.environ

    return True


def _colorize(text, code):
    return f"\033[{code}m{text}\033[0m" if _supports_color() else text


def _bold(text):
    return f"\033[1m{text}\033[0m" if _supports_color() else text


def _skapersok_ascii_art_core():
    return art.text2art("Skapersok", chr_ignore=True)


def _skapersok_ascii_art(width: int):
    skapersok = _skapersok_ascii_art_core()
    skapersok = "\n".join(s.center(width) for s in skapersok.split("\n"))
    return skapersok


def _welcome_section(divider: str) -> str:
    width = len(divider)
    skapersok = "\n".join(line.center(width) for line in _skapersok_ascii_art(width).split("\n"))
    version_line = f"v{constants.version}".center(width)

    return "\n".join(
        [
            "",
            _colorize(divider, "2"),
            _colorize(skapersok, "96"),
            _colorize(divider, "2"),
            _colorize(version_line, "92"),
            _colorize(divider, "2"),
            "",
            "Welcome to the Skapersøk backend!".center(width),
            "For help, please visit: https://docs.skapersok.no/".center(width),
            "",
            _colorize(divider, "2"),
        ]
    )


def _browser_section(divider: str) -> str:
    if not constants.in_docker and settings.autoopen_browser:
        line_length = len(divider)
        return "\n".join(
            [
                "",
                "A browser window should have opened. If not, please visit:".center(line_length),
                constants.local_server_url.center(line_length),
                "",
                _colorize(divider, "2"),
            ]
        )
    return ""


def _database_section(divider: str) -> str:
    line_length = len(divider)
    if not some_database():
        password = auth.DefaultAdminUser.password
        username = auth.DefaultAdminUser.username
        return "\n".join(
            [
                _bold("No database found. A new one will be created.".center(line_length)),
                "",
                _bold(
                    f"A user with username '{username}' and password '{password}' will be created.".center(
                        line_length
                    )
                ),
                "",
                _colorize(divider, "2"),
            ]
        )
    elif auth.DefaultAdminUser.exists():
        return "\n".join(
            [
                "",
                "There is a default admin user with the".center(line_length),
                f"username '{auth.DefaultAdminUser.username}' and password '{auth.DefaultAdminUser.password}'.".center(
                    line_length
                ),
                _colorize(
                    _bold("Please change the password as soon as possible.".center(line_length)),
                    "91",
                ),
                "",
                _colorize(divider, "2"),
            ]
        )
    return ""


def print_banner():
    width = len(_skapersok_ascii_art_core().splitlines()[0])
    divider = "─" * (width + 10)
    sections = [
        _welcome_section(divider),
        _browser_section(divider),
        _database_section(divider),
    ]

    print("\n".join(section for section in sections if section))
