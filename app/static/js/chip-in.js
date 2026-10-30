// Prefill the typed amount into each pay-app link. Without JS the links still open the app.
const amount = document.getElementById("chip-amount");
const links = document.querySelectorAll("[data-amount-sep]");
links.forEach((link) => { link.dataset.base = link.getAttribute("href"); });

amount?.addEventListener("input", () => {
  const value = Number.parseFloat(amount.value.replace(/[$,\s]/g, ""));
  const valid = value > 0 && value <= 1000;
  links.forEach((link) => {
    const suffix = valid ? link.dataset.amountSep + value.toFixed(2) : "";
    link.setAttribute("href", link.dataset.base + suffix);
  });
});
