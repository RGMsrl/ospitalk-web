// Draft translations of the legal pages, reached from the app's links (?lang=xx).
// Only pages listed here exist: the others stay on the Italian text, which is the only binding one.
(function () {
  var drafts = {
    en: ["termini.html", "privacy.html", "dpa.html"],
    es: ["termini.html", "privacy.html", "dpa.html"],
    pt: ["termini.html", "privacy.html", "dpa.html"],
  };
  var lang = new URLSearchParams(location.search).get("lang");
  var page = location.pathname.replace(/^\//, "") || "index.html";
  if (lang && drafts[lang] && drafts[lang].indexOf(page) !== -1) {
    location.replace("/" + lang + "/" + page + location.hash);
  }
})();
