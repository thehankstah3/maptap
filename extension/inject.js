// Runs in the page's own JS context (world: MAIN) so it can patch the
// real navigator.clipboard before maptap.gg's own scripts call it.
// maptap.gg's "copy" button uses Clipboard API writeText(), which does NOT
// fire a DOM "copy" event — so we intercept the call directly instead.
(function () {
  const original = navigator.clipboard.writeText.bind(navigator.clipboard);
  navigator.clipboard.writeText = function (text) {
    window.postMessage({ source: "maptap-ext-clipboard", text }, "*");
    return original(text);
  };
})();
