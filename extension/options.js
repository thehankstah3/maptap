const FIELDS = ["playerName", "chats", "apiKey"];

chrome.storage.sync.get(FIELDS, (cfg) => {
  FIELDS.forEach((f) => {
    if (cfg[f]) document.getElementById(f).value = cfg[f];
  });
});

document.getElementById("save").addEventListener("click", () => {
  const values = {};
  FIELDS.forEach((f) => {
    values[f] = document.getElementById(f).value.trim();
  });
  chrome.storage.sync.set(values, () => {
    const status = document.getElementById("status");
    status.textContent = "Saved.";
    setTimeout(() => (status.textContent = ""), 2000);
  });
});
