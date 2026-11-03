// Prefill the typed amount into each pay-app link. Without JS the links still open the app.
const amount = document.getElementById("chip-amount");
const error = document.getElementById("chip-amount-error");
const method = document.getElementById("method");
const links = document.querySelectorAll("[data-amount-sep]");

function parsed() {
  // Same rule as the server: commas only as thousands separators, so 5,50 is an error.
  const text = amount.value.replace(/[$\s]/g, "");
  const ok = /^(\d+|\d{1,3}(,\d{3})+)(\.\d{1,2})?$/.test(text);
  const value = ok ? Number(text.replaceAll(",", "")) : NaN;
  return { text, valid: value >= 0.01 && value <= Number(amount.dataset.max), value };
}

function syncLinks() {
  const { valid, value } = parsed();
  links.forEach((link) => {
    const suffix = valid ? link.dataset.amountSep + value.toFixed(2) : "";
    link.setAttribute("href", link.dataset.base + suffix);
  });
}

if (amount) {
  links.forEach((link) => {
    link.dataset.base = link.getAttribute("href");
    // Paying with an app picks that app for "I sent it".
    link.addEventListener("click", () => { if (method) method.value = link.dataset.method; });
  });
  amount.addEventListener("input", () => {
    syncLinks();
    const { text, valid } = parsed();
    // Only change the alert when it flips, so screen readers don't repeat it on each key.
    if (error.textContent !== error.dataset.message) error.textContent = error.dataset.message;
    const hidden = valid || text === "";
    if (error.hidden !== hidden) error.hidden = hidden;
    if (error.hidden) amount.removeAttribute("aria-invalid");
    else amount.setAttribute("aria-invalid", "true");
  });
  window.addEventListener("pageshow", syncLinks);
}
