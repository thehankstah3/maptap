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
