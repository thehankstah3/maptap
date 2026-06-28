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
        }).then(async (res) => ({ ok: res.ok, inserted: res.ok && (await res.json()).inserted }))
      )
    )
      .then((results) => {
        const allOk = results.every((r) => r.ok);
        const anyInserted = results.some((r) => r.inserted);
        let text, color;
        if (!allOk) {
          text = "!"; color = "#dc2626";
        } else if (!anyInserted) {
          text = "DUP"; color = "#ca8a04";
        } else {
          text = "✓"; color = "#16a34a";
        }
        chrome.action.setBadgeText({ text });
        chrome.action.setBadgeBackgroundColor({ color });
        setTimeout(() => chrome.action.setBadgeText({ text: "" }), 4000);
      })
      .catch((err) => console.error("MapTap Score Logger: failed to submit score", err));
  });
});
