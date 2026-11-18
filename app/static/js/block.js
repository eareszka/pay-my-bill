// Block asks first, in place (#257): the first tap shows the question, Cancel puts the button back.
document.querySelectorAll("form.block-form").forEach((form) => {
  const ask = form.querySelector(".block-ask");
  const question = form.querySelector(".block-confirm");
  if (!ask || !question) return;
  ask.type = "button";
  const asking = (on) => {
    ask.hidden = on;
    question.hidden = !on;
    (on ? question.querySelector(".btn-danger") : ask).focus();
  };
  ask.addEventListener("click", () => asking(true));
  form.querySelector(".block-cancel").addEventListener("click", () => asking(false));
});
