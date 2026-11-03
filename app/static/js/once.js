// A double tap on the submit button sends the form only once.
const RETRY_AFTER_MS = 15000;
const forms = document.querySelectorAll("form[data-once]");
const button = (form) => form.querySelector("button[type=submit]");

forms.forEach((form) => {
  form.addEventListener("submit", () => {
    button(form).disabled = true;
    // If the request stalls or is stopped, the poster can still send it again.
    setTimeout(() => { button(form).disabled = false; }, RETRY_AFTER_MS);
  });
});

// Coming back to the page must leave the button usable.
window.addEventListener("pageshow", () => {
  forms.forEach((form) => { button(form).disabled = false; });
});
