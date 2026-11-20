/* Selettore della lingua: il <details> funziona già da solo (clic, Invio, Spazio).
   Qui solo due comodità: chiusura con Esc e con un clic fuori dal menu. */
(function () {
  function openMenus() { return document.querySelectorAll('details.lang-switch[open]'); }
  document.addEventListener('click', function (e) {
    openMenus().forEach(function (d) { if (!d.contains(e.target)) d.open = false; });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    openMenus().forEach(function (d) {
      var inside = d.contains(document.activeElement);
      d.open = false;
      if (inside) d.querySelector('summary').focus();
    });
  });
})();
