// Share an ask (#288): the phone's share sheet, else copy the link.
for (const button of document.querySelectorAll("[data-share]:not([data-share-ready])")) {
  if (!navigator.share && !navigator.clipboard) continue;
  button.dataset.shareReady = "";
  button.hidden = false;
  const status = button.parentElement.querySelector(".share-status");
  button.addEventListener("click", async () => {
    const url = button.dataset.share;
    if (navigator.share) {
      try {
        await navigator.share({ title: button.dataset.shareTitle, url });
      } catch {
        // Closed without sharing.
      }
      return;
    }
    try {
      await navigator.clipboard.writeText(url);
      status.textContent = "Link copied";
    } catch {
      status.textContent = "Couldn't copy the link";
    }
  });
}
