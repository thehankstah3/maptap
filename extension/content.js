const SIMPLE_GAME_PARSERS = [
  ["wend", parseWendScore],
  ["zip", parseZipScore],
  ["patches", parsePatchesScore],
  ["tango", parseTangoScore],
  ["queens", parseQueensScore],
];

function handleText(text) {
  const maptap = parseMaptapScore(text);
  if (maptap) {
    chrome.runtime.sendMessage({
      type: "RESULT_DETECTED",
      game: "maptap",
      date: maptap.date,
      data: { rounds: maptap.rounds },
      score: maptap.total,
    });
    return;
  }

  const wordle = parseWordleScore(text);
  if (wordle) {
    chrome.runtime.sendMessage({
      type: "RESULT_DETECTED",
      game: "wordle",
      date: new Date().toISOString().slice(0, 10),
      data: wordle,
      score: wordle.attempts,
    });
    return;
  }

  for (const [game, parseFn] of SIMPLE_GAME_PARSERS) {
    const parsed = parseFn(text);
    if (parsed) {
      chrome.runtime.sendMessage({
        type: "RESULT_DETECTED",
        game,
        date: new Date().toISOString().slice(0, 10),
        data: parsed,
        score: parsed.score,
      });
      return;
    }
  }
}

// Bridge from inject.js (page context) to this isolated-world content script.
window.addEventListener("message", (event) => {
  if (event.source !== window) return;
  if (event.data && event.data.source === "maptap-ext-clipboard") {
    handleText(event.data.text);
  }
});

// Fallback for manual Ctrl+C copies of selected text.
document.addEventListener("copy", () => {
  handleText(window.getSelection().toString());
});
