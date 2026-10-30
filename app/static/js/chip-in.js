// Prefill the typed amount into each pay-app link. Without JS the links still open the app.
const amount = document.getElementById("chip-amount");
const error = document.getElementById("chip-amount-error");
const links = document.querySelectorAll("[data-amount-sep]");
links.forEach((link) => { link.dataset.base = link.getAttribute("href"); });

function sync() {
  const text = amount.value.replace(/[$\s]/g, "");
  const value = /^\d+(\.\d{1,2})?$/.test(text) ? Number(text) : NaN;
  const valid = value >= 0.01 && value <= 1000;
  links.forEach((link) => {
    const suffix = valid ? link.dataset.amountSep + value.toFixed(2) : "";
    link.setAttribute("href", link.dataset.base + suffix);
  });
  error.hidden = valid || text === "";
}

if (amount) {
  amount.addEventListener("input", sync);
  window.addEventListener("pageshow", sync);
}
