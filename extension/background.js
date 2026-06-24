const DEFAULT_API_BASE = "https://superb-nurturing-production-f3fc.up.railway.app";

chrome.runtime.onMessage.addListener((message) => {
  if (message.type !== "SCORE_DETECTED") return;

  chrome.storage.sync.get(["playerName", "chatName", "apiKey", "apiBase"], (cfg) => {
    if (!cfg.playerName || !cfg.chatName || !cfg.apiKey) {
      console.warn("MapTap Score Logger: open the extension popup and set player/chat/API key first.");
      return;
    }

    fetch(`${cfg.apiBase || DEFAULT_API_BASE}/api/scores`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": cfg.apiKey },
      body: JSON.stringify({ chat: cfg.chatName, player: cfg.playerName, ...message.payload }),
    })
      .then((res) => {
        const ok = res.ok;
        chrome.action.setBadgeText({ text: ok ? "✓" : "!" });
        chrome.action.setBadgeBackgroundColor({ color: ok ? "#16a34a" : "#dc2626" });
        setTimeout(() => chrome.action.setBadgeText({ text: "" }), 4000);
      })
      .catch((err) => console.error("MapTap Score Logger: failed to submit score", err));
  });
});
