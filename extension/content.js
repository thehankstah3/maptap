function handleText(text) {
  const parsed = parseMaptapScore(text);
  if (parsed) {
    chrome.runtime.sendMessage({ type: "SCORE_DETECTED", payload: parsed });
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
