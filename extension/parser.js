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

function noOrNum(s) {
  return s.toLowerCase() === "no" ? 0 : parseInt(s, 10);
}

function timeToSeconds(timeStr) {
  return timeStr.split(":").reduce((acc, part) => acc * 60 + parseInt(part, 10), 0);
}

const TIME_RE = "([\\d:]+)";
const WEND_RE = new RegExp("Wend\\s+#(\\d+)\\s*\\|\\s*" + TIME_RE + "\\s*🌀", "i");
const WEND_DETAIL_RE = /With\s+(no|\d+)\s+hints?\s*&\s*(no|\d+)\s+backtracks/i;
const ZIP_RE = new RegExp("Zip\\s+#(\\d+)\\s*\\|\\s*" + TIME_RE + "\\s*🏁", "i");
const ZIP_DETAIL_RE = /With\s+(no|\d+)\s+backtracks/i;
const PATCHES_RE = new RegExp("Patches\\s+#(\\d+)\\s*\\|\\s*" + TIME_RE + "\\s*🧶", "i");
const PATCHES_DETAIL_RE = /With\s+(no|\d+)\s+hints?\s*&\s*(no|\d+)\s+redraws/i;
const TANGO_RE = new RegExp("Tango\\s+#(\\d+)\\s*\\|\\s*" + TIME_RE, "i");
const QUEENS_RE = new RegExp("Queens\\s+#(\\d+)\\s*\\|\\s*" + TIME_RE, "i");
const HINTS_RE = /with\s+(no|\d+)\s+hints/i;

// The hints/backtracks/redraws detail line is sometimes omitted by
// LinkedIn's share text, so each is matched separately and merged in
// only when present, rather than required by the main pattern.
function parseWendScore(content) {
  const m = content && content.match(WEND_RE);
  if (!m) return null;
  const result = { puzzle: parseInt(m[1], 10), score: timeToSeconds(m[2]) };
  const d = content.match(WEND_DETAIL_RE);
  if (d) { result.hints = noOrNum(d[1]); result.backtracks = noOrNum(d[2]); }
  return result;
}

function parseZipScore(content) {
  const m = content && content.match(ZIP_RE);
  if (!m) return null;
  const result = { puzzle: parseInt(m[1], 10), score: timeToSeconds(m[2]) };
  const d = content.match(ZIP_DETAIL_RE);
  if (d) result.backtracks = noOrNum(d[1]);
  return result;
}

function parsePatchesScore(content) {
  const m = content && content.match(PATCHES_RE);
  if (!m) return null;
  const result = { puzzle: parseInt(m[1], 10), score: timeToSeconds(m[2]) };
  const d = content.match(PATCHES_DETAIL_RE);
  if (d) { result.hints = noOrNum(d[1]); result.redraws = noOrNum(d[2]); }
  return result;
}

function parseTangoScore(content) {
  const m = content && content.match(TANGO_RE);
  if (!m) return null;
  const result = { puzzle: parseInt(m[1], 10), score: timeToSeconds(m[2]) };
  const h = content.match(HINTS_RE);
  if (h) result.hints = noOrNum(h[1]);
  return result;
}

function parseQueensScore(content) {
  const m = content && content.match(QUEENS_RE);
  if (!m) return null;
  const result = { puzzle: parseInt(m[1], 10), score: timeToSeconds(m[2]) };
  const h = content.match(HINTS_RE);
  if (h) result.hints = noOrNum(h[1]);
  return result;
}
