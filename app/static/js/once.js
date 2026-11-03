// A double tap on the submit button sends the form only once.
const forms = document.querySelectorAll("form[data-once]");

forms.forEach((form) => {
  form.addEventListener("submit", () => {
    form.querySelector("button[type=submit]").disabled = true;
  });
});

// Coming back to the page must leave the button usable.
window.addEventListener("pageshow", () => {
  forms.forEach((form) => {
    form.querySelector("button[type=submit]").disabled = false;
  });
});
