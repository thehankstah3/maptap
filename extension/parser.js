// Mirrors bot/parser.py's parse_maptap_message logic for the browser.
function parseMaptapScore(content) {
  if (!content || !content.toLowerCase().includes("maptap.gg")) return null;

  const parts = content.split(/[/\n]/).map((s) => s.trim()).filter(Boolean);
  if (parts.length < 3) return null;

  const dateMatch = parts[0].match(/([A-Za-z]+\s+\d{1,2})/);
  const totalMatch = parts[2].match(/Final score:\s*(\d+)/i);
  const rounds = (parts[1].match(/\d+/g) || []).map(Number);
  if (!dateMatch || !totalMatch || rounds.length === 0) return null;

  const year = new Date().getFullYear();
  const parsedDate = new Date(`${dateMatch[1]} ${year}`);
  if (isNaN(parsedDate.getTime())) return null;

  return {
    date: parsedDate.toISOString().slice(0, 10),
    rounds,
    total: parseInt(totalMatch[1], 10),
  };
}

const WORDLE_RE = /Wordle\s+[\d,]+\s+(X|[1-6])\/6/i;
const GRID_LINE_RE = /^[⬛⬜🟨🟩]{5}$/u;

function parseWordleScore(content) {
  if (!content) return null;
  const match = content.match(WORDLE_RE);
  if (!match) return null;

  const attemptsRaw = match[1].toUpperCase();
  const attempts = attemptsRaw === "X" ? 7 : parseInt(attemptsRaw, 10);

  const grid = content
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => GRID_LINE_RE.test(line));
  if (grid.length === 0) return null;

  return { attempts, grid };
}
