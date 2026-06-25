import re
from datetime import datetime

MONTH_DAY_RE = re.compile(r"([A-Za-z]+\s+\d{1,2})")
TOTAL_RE = re.compile(r"Final score:\s*(\d+)", re.IGNORECASE)


def parse_maptap_message(content, year):
    """Parse a maptap.gg result message into (date_str, rounds, total).

    Expected format (fields separated by '/' or newlines):
        www.maptap.gg June 22
        99🎯 100🎯 98🎯 91👑 88🎉
        Final score: 932

    Returns None if the message doesn't match.
    """
    if "maptap.gg" not in content.lower():
        return None

    parts = [p.strip() for p in re.split(r"[/\n]", content) if p.strip()]
    if len(parts) < 3:
        return None

    date_match = MONTH_DAY_RE.search(parts[0])
    total_match = TOTAL_RE.search(parts[2])
    rounds = [int(n) for n in re.findall(r"\d+", parts[1])]

    if not date_match or not total_match or not rounds:
        return None

    try:
        parsed_date = datetime.strptime(f"{date_match.group(1)} {year}", "%B %d %Y").date()
    except ValueError:
        return None

    return {
        "date": parsed_date.isoformat(),
        "rounds": rounds,
        "total": int(total_match.group(1)),
    }


WORDLE_RE = re.compile(r"Wordle\s+[\d,]+\s+(X|[1-6])/6", re.IGNORECASE)
GRID_LINE_RE = re.compile(r"^[⬛⬜\U0001F7E8\U0001F7E9]{5}$")


def parse_wordle_message(content):
    """Parse a Wordle share message, e.g.:
        Wordle 1,234 4/6

        ⬜⬜🟨⬜⬜
        ⬜⬜🟩⬜⬜
        ⬜🟩🟩⬜⬜
        🟩🟩🟩🟩🟩

    A failed game (X/6) scores as 7 attempts so "fewer is better" sorting
    still ranks it worst. Returns None if the message doesn't match.
    """
    match = WORDLE_RE.search(content)
    if not match:
        return None

    attempts_raw = match.group(1).upper()
    attempts = 7 if attempts_raw == "X" else int(attempts_raw)

    grid = [line.strip() for line in content.splitlines() if GRID_LINE_RE.match(line.strip())]
    if not grid:
        return None

    return {"attempts": attempts, "grid": grid}


def _no_or_num(s):
    return 0 if s.lower() == "no" else int(s)


def _mmss_to_seconds(mm, ss):
    return int(mm) * 60 + int(ss)


WEND_RE = re.compile(
    r"Wend\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*🌀.*?With\s+(no|\d+)\s+hints?\s*&\s*(no|\d+)\s+backtracks",
    re.IGNORECASE | re.DOTALL,
)
ZIP_RE = re.compile(
    r"Zip\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*🏁.*?With\s+(no|\d+)\s+backtracks",
    re.IGNORECASE | re.DOTALL,
)
PATCHES_RE = re.compile(
    r"Patches\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*🧶.*?With\s+(no|\d+)\s+hints?\s*&\s*(no|\d+)\s+redraws",
    re.IGNORECASE | re.DOTALL,
)
TANGO_RE = re.compile(r"Tango\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*with\s+(no|\d+)\s+hints", re.IGNORECASE)
QUEENS_RE = re.compile(r"Queens\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*with\s+(no|\d+)\s+hints", re.IGNORECASE)


def parse_wend_message(content):
    """Wend #16 | 1:01 🌀\nWith no hints & 3 backtracks\nlnkd.in/wend."""
    match = WEND_RE.search(content)
    if not match:
        return None
    puzzle, mm, ss, hints, backtracks = match.groups()
    return {
        "puzzle": int(puzzle),
        "score": _mmss_to_seconds(mm, ss),
        "hints": _no_or_num(hints),
        "backtracks": _no_or_num(backtracks),
    }


def parse_zip_message(content):
    """Zip #464 | 2:28 🏁\nWith 17 backtracks 🛑\nlnkd.in/zip."""
    match = ZIP_RE.search(content)
    if not match:
        return None
    puzzle, mm, ss, backtracks = match.groups()
    return {"puzzle": int(puzzle), "score": _mmss_to_seconds(mm, ss), "backtracks": _no_or_num(backtracks)}


def parse_patches_message(content):
    """Patches #99 | 0:46 🧶\nWith no hints & 8 redraws\nlnkd.in/patches."""
    match = PATCHES_RE.search(content)
    if not match:
        return None
    puzzle, mm, ss, hints, redraws = match.groups()
    return {
        "puzzle": int(puzzle),
        "score": _mmss_to_seconds(mm, ss),
        "hints": _no_or_num(hints),
        "redraws": _no_or_num(redraws),
    }


def parse_tango_message(content):
    """Tango #625 | 1:15 with no hints\nFirst 5 placements:\n...\nlnkd.in/tango."""
    match = TANGO_RE.search(content)
    if not match:
        return None
    puzzle, mm, ss, hints = match.groups()
    return {"puzzle": int(puzzle), "score": _mmss_to_seconds(mm, ss), "hints": _no_or_num(hints)}


def parse_queens_message(content):
    """Queens #785 | 0:32 with no hints\nFirst 👑s: 🟦 🟥 🟨\nlnkd.in/queens."""
    match = QUEENS_RE.search(content)
    if not match:
        return None
    puzzle, mm, ss, hints = match.groups()
    return {"puzzle": int(puzzle), "score": _mmss_to_seconds(mm, ss), "hints": _no_or_num(hints)}
