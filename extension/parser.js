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

function mmssToSeconds(mm, ss) {
  return parseInt(mm, 10) * 60 + parseInt(ss, 10);
}

const WEND_RE = /Wend\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*🌀[\s\S]*?With\s+(no|\d+)\s+hints?\s*&\s*(no|\d+)\s+backtracks/i;
const ZIP_RE = /Zip\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*🏁[\s\S]*?With\s+(no|\d+)\s+backtracks/i;
const PATCHES_RE = /Patches\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*🧶[\s\S]*?With\s+(no|\d+)\s+hints?\s*&\s*(no|\d+)\s+redraws/i;
const TANGO_RE = /Tango\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*with\s+(no|\d+)\s+hints/i;
const QUEENS_RE = /Queens\s+#(\d+)\s*\|\s*(\d+):(\d+)\s*with\s+(no|\d+)\s+hints/i;

function parseWendScore(content) {
  const m = content && content.match(WEND_RE);
  if (!m) return null;
  return { puzzle: parseInt(m[1], 10), score: mmssToSeconds(m[2], m[3]), hints: noOrNum(m[4]), backtracks: noOrNum(m[5]) };
}

function parseZipScore(content) {
  const m = content && content.match(ZIP_RE);
  if (!m) return null;
  return { puzzle: parseInt(m[1], 10), score: mmssToSeconds(m[2], m[3]), backtracks: noOrNum(m[4]) };
}

function parsePatchesScore(content) {
  const m = content && content.match(PATCHES_RE);
  if (!m) return null;
  return { puzzle: parseInt(m[1], 10), score: mmssToSeconds(m[2], m[3]), hints: noOrNum(m[4]), redraws: noOrNum(m[5]) };
}

function parseTangoScore(content) {
  const m = content && content.match(TANGO_RE);
  if (!m) return null;
  return { puzzle: parseInt(m[1], 10), score: mmssToSeconds(m[2], m[3]), hints: noOrNum(m[4]) };
}

function parseQueensScore(content) {
  const m = content && content.match(QUEENS_RE);
  if (!m) return null;
  return { puzzle: parseInt(m[1], 10), score: mmssToSeconds(m[2], m[3]), hints: noOrNum(m[4]) };
}
