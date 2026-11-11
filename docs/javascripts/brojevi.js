// Brojevi poglavlja i odjeljaka dobivaju vlastiti <span> da ih CSS može obojiti.
// Markdown ostaje netaknut ("# 4. Naslov", "## 4.1 Naslov"), pa se na GitHubu
// prikazuje kao i prije; ovo radi samo na GitHub Pages stranici.
//
//   h1  "4. Naslov"    -> <span class="oo-badge">4</span> Naslov
//   h2  "4.1 Naslov"   -> <span class="oo-num">4.1</span> Naslov
//   nav "4. Naslov"    -> <span class="oo-nav-num">4</span> Naslov

(function () {
  var RE_H1 = /^\s*(\d+)\.\s+/;          // "4. "
  var RE_H2 = /^\s*(\d+(?:\.\d+)+)\s+/;  // "4.1 ", "5.11 "
  var RE_NAV = /^\s*(\d+)\.\s+/;         // "4. " u navigaciji

  // prvi tekstni čvor elementa (preskače prazne čvorove)
  function firstText(el) {
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        return n.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_SKIP;
      }
    });
    return walker.nextNode();
  }

  function wrap(el, re, cls, label) {
    if (el.dataset.ooNum) return;        // već obrađeno
    var node = firstText(el);
    if (!node) return;
    var m = node.nodeValue.match(re);
    if (!m) return;
    var span = document.createElement("span");
    span.className = cls;
    span.textContent = label ? label(m[1]) : m[1];
    node.nodeValue = node.nodeValue.slice(m[0].length);
    node.parentNode.insertBefore(span, node);
    el.dataset.ooNum = "1";
  }

  function apply() {
    document.querySelectorAll(".md-typeset h1").forEach(function (h) {
      wrap(h, RE_H1, "oo-badge");
    });
    document.querySelectorAll(".md-typeset h2").forEach(function (h) {
      wrap(h, RE_H2, "oo-num");
    });
    // samo poglavlja (stavke koje su stranice), ne odjeljci integriranog sadržaja
    document.querySelectorAll(".md-nav--primary .md-nav__item > .md-nav__link .md-ellipsis")
      .forEach(function (s) { wrap(s, RE_NAV, "oo-nav-num"); });
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(apply);
  } else {
    document.addEventListener("DOMContentLoaded", apply);
  }
})();
