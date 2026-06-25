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


WEND_RE = re.compile(r"Wend\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*🌀", re.IGNORECASE)
WEND_DETAIL_RE = re.compile(r"With\s+(no|\d+)\s+hints?\s*&\s*(no|\d+)\s+backtracks", re.IGNORECASE)
ZIP_RE = re.compile(r"Zip\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*🏁", re.IGNORECASE)
ZIP_DETAIL_RE = re.compile(r"With\s+(no|\d+)\s+backtracks", re.IGNORECASE)
PATCHES_RE = re.compile(r"Patches\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*🧶", re.IGNORECASE)
PATCHES_DETAIL_RE = re.compile(r"With\s+(no|\d+)\s+hints?\s*&\s*(no|\d+)\s+redraws", re.IGNORECASE)
TANGO_RE = re.compile(r"Tango\s+#(\d+)\s*\|\s*(\d+):(\d+)", re.IGNORECASE)
QUEENS_RE = re.compile(r"Queens\s+#(\d+)\s*\|\s*(\d+):(\d+)", re.IGNORECASE)
HINTS_RE = re.compile(r"with\s+(no|\d+)\s+hints", re.IGNORECASE)


def parse_wend_message(content):
    """Wend #16 | 1:01 🌀\n[With no hints & 3 backtracks\n]lnkd.in/wend.

    The hints/backtracks line is sometimes omitted by LinkedIn's share text,
    so it's optional — only included in the result when present.
    """
    match = WEND_RE.search(content)
    if not match:
        return None
    puzzle, mm, ss = match.groups()
    result = {"puzzle": int(puzzle), "score": _mmss_to_seconds(mm, ss)}
    detail = WEND_DETAIL_RE.search(content)
    if detail:
        result["hints"] = _no_or_num(detail.group(1))
        result["backtracks"] = _no_or_num(detail.group(2))
    return result


def parse_zip_message(content):
    """Zip #464 | 2:28 🏁\n[With 17 backtracks 🛑\n]lnkd.in/zip."""
    match = ZIP_RE.search(content)
    if not match:
        return None
    puzzle, mm, ss = match.groups()
    result = {"puzzle": int(puzzle), "score": _mmss_to_seconds(mm, ss)}
    detail = ZIP_DETAIL_RE.search(content)
    if detail:
        result["backtracks"] = _no_or_num(detail.group(1))
    return result


def parse_patches_message(content):
    """Patches #99 | 0:46 🧶\n[With no hints & 8 redraws\n]lnkd.in/patches."""
    match = PATCHES_RE.search(content)
    if not match:
        return None
    puzzle, mm, ss = match.groups()
    result = {"puzzle": int(puzzle), "score": _mmss_to_seconds(mm, ss)}
    detail = PATCHES_DETAIL_RE.search(content)
    if detail:
        result["hints"] = _no_or_num(detail.group(1))
        result["redraws"] = _no_or_num(detail.group(2))
    return result


def parse_tango_message(content):
    """Tango #625 | 1:15 [with no hints]\nFirst 5 placements:\n...\nlnkd.in/tango."""
    match = TANGO_RE.search(content)
    if not match:
        return None
    puzzle, mm, ss = match.groups()
    result = {"puzzle": int(puzzle), "score": _mmss_to_seconds(mm, ss)}
    hints = HINTS_RE.search(content)
    if hints:
        result["hints"] = _no_or_num(hints.group(1))
    return result


def parse_queens_message(content):
    """Queens #785 | 0:32 [with no hints]\nFirst 👑s: 🟦 🟥 🟨\nlnkd.in/queens."""
    match = QUEENS_RE.search(content)
    if not match:
        return None
    puzzle, mm, ss = match.groups()
    result = {"puzzle": int(puzzle), "score": _mmss_to_seconds(mm, ss)}
    hints = HINTS_RE.search(content)
    if hints:
        result["hints"] = _no_or_num(hints.group(1))
    return result
