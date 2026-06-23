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
