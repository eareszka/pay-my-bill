// Share an ask (#288): the phone's share sheet, else copy the link.
const COPIED_MS = 2500;

for (const button of document.querySelectorAll("[data-share]:not([data-share-ready])")) {
  if (!navigator.share && !navigator.clipboard) continue;
  button.dataset.shareReady = "";
  button.hidden = false;
  const status = button.parentElement.querySelector(".share-status");
  let clear;
  button.addEventListener("click", async () => {
    const url = button.dataset.share;
    if (navigator.share) {
      try {
        await navigator.share({ title: button.dataset.shareTitle, url });
        return;
      } catch (error) {
        // Closed without sharing. Anything else (NotAllowedError in the iOS shell) falls back to copying.
        if (error.name === "AbortError") return;
      }
    }
    // Emptied first, so a second copy is announced again.
    status.textContent = "";
    clearTimeout(clear);
    try {
      await navigator.clipboard.writeText(url);
      status.textContent = "Link copied";
    } catch {
      status.textContent = "Couldn't copy the link";
    }
    clear = setTimeout(() => { status.textContent = ""; }, COPIED_MS);
  });
}
