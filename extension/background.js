const DEFAULT_API_BASE = "https://superb-nurturing-production-f3fc.up.railway.app";

chrome.runtime.onMessage.addListener((message) => {
  if (message.type !== "RESULT_DETECTED") return;

  chrome.storage.sync.get(["playerName", "chats", "apiKey", "apiBase"], (cfg) => {
    const chatList = (cfg.chats || "").split(",").map((c) => c.trim()).filter(Boolean);
    if (!cfg.playerName || !chatList.length || !cfg.apiKey) {
      console.warn("MapTap Score Logger: open the extension popup and set player/chats/API key first.");
      return;
    }

    const apiBase = cfg.apiBase || DEFAULT_API_BASE;
    Promise.all(
      chatList.map((chat) =>
        fetch(`${apiBase}/api/results`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-API-Key": cfg.apiKey },
          body: JSON.stringify({
            game: message.game,
            chat,
            player: cfg.playerName,
            date: message.date,
            data: message.data,
            score: message.score,
          }),
        }).then((res) => res.ok)
      )
    )
      .then((results) => {
        const ok = results.every(Boolean);
        chrome.action.setBadgeText({ text: ok ? "✓" : "!" });
        chrome.action.setBadgeBackgroundColor({ color: ok ? "#16a34a" : "#dc2626" });
        setTimeout(() => chrome.action.setBadgeText({ text: "" }), 4000);
      })
      .catch((err) => console.error("MapTap Score Logger: failed to submit score", err));
  });
});
