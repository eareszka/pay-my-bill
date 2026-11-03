// Prefill the typed amount into each pay-app link, and remember it while the donor is in
// their payment app. Without JS the links still open the app and the whole form stays visible.
const form = document.querySelector("form.chip-in");
const amount = document.getElementById("chip-amount");
const error = document.getElementById("chip-amount-error");
const method = document.getElementById("method");
const question = document.getElementById("sent-question");
const notYet = document.getElementById("not-yet");
const links = document.querySelectorAll("[data-amount-sep]");
const key = form ? `chip-in:${form.dataset.post}` : "";

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

// Storage can be unavailable in private modes; the form still works, it just won't remember.
function load() {
  try {
    return JSON.parse(sessionStorage.getItem(key)) || {};
  } catch {
    return {};
  }
}

function save(state) {
  try {
    sessionStorage.setItem(key, JSON.stringify(state));
  } catch {
    // Nothing to do: see load().
  }
}

function clear(recordedKey) {
  try {
    sessionStorage.removeItem(recordedKey);
  } catch {
    // Nothing to do: see load().
  }
}

function showSentStep(label, handle) {
  const { value } = parsed();
  const shown = Number.isInteger(value) ? String(value) : value.toFixed(2);
  question.textContent = `Sent $${shown} to ${handle} on ${label}?`;
  question.hidden = false;
  notYet.hidden = false;
  form.dataset.step = "sent";
}

function showPayStep() {
  question.hidden = true;
  notYet.hidden = true;
  delete form.dataset.step;
}

function restore() {
  const state = load();
  if (state.amount && !amount.value) amount.value = state.amount;
  syncLinks();
  // A server error needs the whole form, and logged-out visitors have nothing to record yet.
  if (!state.paid || !method || form.querySelector("[aria-invalid=true]")) return;
  method.value = state.paid;
  // The app may be gone if the poster removed it since; then the donor picks another.
  if (method.value === state.paid && parsed().valid) showSentStep(state.label, state.handle);
}

if (amount) {
  links.forEach((link) => {
    link.dataset.base = link.getAttribute("href");
    link.addEventListener("click", () => {
      // Paying with an app picks that app for "I sent it".
      if (method) method.value = link.dataset.method;
      if (!parsed().valid) return;
      const { method: paid, label, handle } = link.dataset;
      save({ amount: amount.value, paid, label, handle });
      if (method) {
        showSentStep(label, handle);
        question.focus();
      }
    });
  });
  amount.addEventListener("input", () => {
    syncLinks();
    const { text, valid } = parsed();
    save({ amount: amount.value });
    // Only change the alert when it flips, so screen readers don't repeat it on each key.
    if (error.textContent !== error.dataset.message) error.textContent = error.dataset.message;
    const hidden = valid || text === "";
    if (error.hidden !== hidden) error.hidden = hidden;
    if (hidden) amount.removeAttribute("aria-invalid");
    else amount.setAttribute("aria-invalid", "true");
  });
  if (notYet) {
    notYet.addEventListener("click", () => {
      save({ amount: amount.value });
      showPayStep();
      amount.focus();
    });
  }
  window.addEventListener("pageshow", restore);
}

// The server has this gift now, so there's nothing left to remember.
const recorded = document.querySelector("[data-gift-recorded]");
if (recorded) {
  clear(`chip-in:${recorded.dataset.giftRecorded}`);
}
