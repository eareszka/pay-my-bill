// Show what the poster gets from a card gift once fees come out (ADR 0016).
// Same math as stripe_pay.split(); without JS the hint below the button explains it.
const input = document.getElementById("card-amount");
const net = document.getElementById("card-net");

function cents(value) {
  return `$${(value / 100).toFixed(2)}`;
}

function update() {
  const text = input.value.replace(/[$\s]/g, "");
  const ok = /^(\d+|\d{1,3}(,\d{3})+)(\.\d{1,2})?$/.test(text);
  const paid = ok ? Math.round(Number(text.replaceAll(",", "")) * 100) : NaN;
  const d = input.dataset;
  if (!(paid >= Number(d.min) * 100 && paid <= Number(d.max) * 100)) {
    net.hidden = true;
    return;
  }
  // Round each fee up to the cent first, as the server does, so float error can't add one.
  const up = (x) => Math.ceil(Math.round(x * 1e6) / 1e6);
  const fee = up(paid * Number(d.cardRate)) + Number(d.cardFixed) + up(paid * Number(d.platformRate));
  net.textContent = `${net.dataset.poster} gets about ${cents(paid - fee)}.`;
  net.hidden = false;
}

if (input && net) {
  input.addEventListener("input", update);
  update();
}
