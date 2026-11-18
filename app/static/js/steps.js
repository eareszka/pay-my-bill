// Shows the new-post form one question at a time. Without JS it stays one long form.
const form = document.querySelector("form.q-form");
const steps = form ? [...form.querySelectorAll("[data-step]")] : [];
const AUTO_NEXT_MS = 250;

if (steps.length) {
  const bar = form.querySelector(".q-progress-bar");
  const back = form.querySelector("[data-q-back]");
  const skip = form.querySelector("[data-q-skip]");
  const next = form.querySelector("[data-q-next]");
  const submit = form.querySelector("[data-q-submit]");
  const inputs = (step) => [...step.querySelectorAll("input, textarea, select")];
  // A server error opens on the first question that needs fixing.
  const failed = steps.findIndex((step) => step.querySelector(".error"));
  let current = Math.max(failed, 0);

  function show(index, focus = true) {
    // The question slides in from the side you're heading to.
    if (index !== current) form.dataset.dir = index > current ? "next" : "back";
    current = index;
    steps.forEach((step, i) => { step.hidden = i !== index; });
    const last = index === steps.length - 1;
    bar.style.width = `${((index + 1) / steps.length) * 100}%`;
    back.hidden = index === 0;
    skip.hidden = last || !("optional" in steps[index].dataset);
    next.hidden = last;
    submit.hidden = !last;
    if (focus) inputs(steps[index])[0]?.focus();
  }

  // Only the question on screen is checked here; the server still checks everything.
  function valid() {
    return inputs(steps[current]).every((input) => input.reportValidity());
  }

  function go(index) {
    history.pushState({ step: index }, "");
    show(index);
  }

  form.dataset.steps = "on";
  form.querySelector(".q-progress").hidden = false;
  history.replaceState({ step: current }, "");
  show(current, failed >= 0);

  next.addEventListener("click", () => { if (valid()) go(current + 1); });
  skip.addEventListener("click", () => go(current + 1));
  back.addEventListener("click", () => history.back());
  window.addEventListener("popstate", (event) => {
    if (typeof event.state?.step === "number") show(event.state.step);
  });

  form.addEventListener("keydown", (event) => {
    // Enter moves to the next question instead of posting early.
    if (event.key !== "Enter" || event.target.tagName === "TEXTAREA" || !next.offsetParent) return;
    event.preventDefault();
    next.click();
  });

  // Picking need/want or a category moves on by itself, like the apps people know.
  form.addEventListener("change", (event) => {
    if (event.target.type !== "radio") return;
    const step = current;
    setTimeout(() => { if (current === step) next.click(); }, AUTO_NEXT_MS);
  });
}
