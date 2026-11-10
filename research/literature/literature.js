/* Catálogo bibliográfico · research/literature
 * Lee data/literature_catalog.csv (fuente única de datos) y construye la tabla
 * con búsqueda, filtros, ordenamiento y paginación. Sin dependencias externas.
 */
(function () {
  "use strict";

  var PAGE_SIZE = 25;
  var CSV_URL = "data/literature_catalog.csv";
  var BLOCK_LABEL = {
    I: "Bloque I · Referencias del anteproyecto doctoral",
    II: "Bloque II · Literatura complementaria"
  };

  var $ = function (id) { return document.getElementById(id); };
  var els = {
    q: $("lit-q"), block: $("lit-block"), cat: $("lit-cat"), status: $("lit-status"),
    sort: $("lit-sort"), lf: $("lit-lf"), reset: $("lit-reset"), count: $("lit-count"),
    tbody: $("littbody"), pager: $("lit-pager"), chips: $("lit-chips"), table: $("littable")
  };
  if (!els.tbody) return;

  var rows = [];
  var categories = [];
  var page = 0;

  // ------------------------------------------------------------------ CSV
  function parseCSV(text) {
    var out = [], row = [], field = "", i = 0, q = false;
    text = text.replace(/^﻿/, "");
    while (i < text.length) {
      var c = text[i];
      if (q) {
        if (c === '"') {
          if (text[i + 1] === '"') { field += '"'; i++; } else { q = false; }
        } else { field += c; }
      } else if (c === '"') { q = true; }
      else if (c === ",") { row.push(field); field = ""; }
      else if (c === "\n" || c === "\r") {
        if (c === "\r" && text[i + 1] === "\n") i++;
        row.push(field); field = "";
        if (row.length > 1 || row[0] !== "") out.push(row);
        row = [];
      } else { field += c; }
      i++;
    }
    if (field !== "" || row.length) { row.push(field); out.push(row); }
    var head = out.shift();
    return out.map(function (r) {
      var o = {};
      head.forEach(function (h, k) { o[h] = (r[k] || "").trim(); });
      return o;
    });
  }

  // -------------------------------------------------------------- helpers
  function norm(s) {
    return (s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }
  function dateValue(d) {
    var m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(d || "");
    return m ? Number(m[3] + m[2] + m[1]) : 0;
  }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
  }
  function extLink(href, text, label) {
    var a = el("a", null, text);
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    if (label) a.setAttribute("aria-label", label);
    return a;
  }
  function plural(n, one, many) { return n + " " + (n === 1 ? one : many); }

  // ----------------------------------------------------------- filtering
  function filtered() {
    var q = norm(els.q.value).trim();
    var terms = q ? q.split(/\s+/) : [];
    var out = rows.filter(function (r) {
      if (els.block.value && r.block !== els.block.value) return false;
      if (els.cat.value && r.primary_category !== els.cat.value) return false;
      if (els.status.value && r.reading_status !== els.status.value) return false;
      if (els.lf.checked && !r.latent_frontiers_url) return false;
      if (!terms.length) return true;
      return terms.every(function (t) { return r._search.indexOf(t) !== -1; });
    });
    var s = els.sort.value;
    var byOrder = function (a, b) { return a._order - b._order; };
    out.sort(function (a, b) {
      if (s === "read-desc") return (dateValue(b.reading_date) - dateValue(a.reading_date)) || byOrder(a, b);
      if (s === "year-desc") return (b._year - a._year) || byOrder(a, b);
      if (s === "year-asc") return (a._year - b._year) || byOrder(a, b);
      return byOrder(a, b);
    });
    return out;
  }

  // ------------------------------------------------------------- render
  function groupKey(r) {
    return r.block === "I" ? "I" : "II|" + r.primary_category;
  }

  function groupRow(r, cont) {
    var tr = el("tr", "lit-group");
    var th = el("th");
    th.colSpan = 6;
    th.scope = "colgroup";
    if (r.block === "I") {
      th.appendChild(el("span", "lit-group-block", BLOCK_LABEL.I));
      th.appendChild(el("span", "lit-group-note", "Orden de la lista «Referencias» del anteproyecto (V4)"));
    } else {
      th.appendChild(el("span", "lit-group-block", BLOCK_LABEL.II));
      th.appendChild(el("span", "lit-group-cat", r.primary_category));
    }
    if (cont) th.appendChild(el("span", "lit-group-note", "(continuación)"));
    tr.appendChild(th);
    return tr;
  }

  function cell(tr, label, cls) {
    var td = el("td", cls);
    td.setAttribute("data-label", label);
    tr.appendChild(td);
    return td;
  }

  function itemRow(r) {
    var tr = el("tr", "lit-row");
    tr.id = r.article_id;

    var n = cell(tr, "N.º", "lit-col-n");
    n.textContent = r.reading_order;

    var item = cell(tr, "Elemento", "lit-col-item");
    var t = el("p", "lit-title", r.title_original);
    t.lang = "en";
    item.appendChild(t);
    if (r.title_es) {
      var es = el("p", "lit-title-es", r.title_es);
      es.lang = "es";
      item.appendChild(es);
    }
    var meta = el("p", "lit-meta");
    meta.appendChild(el("span", "lit-cite", r.citation_short));
    if (r.venue) meta.appendChild(el("span", "lit-venue", r.venue));
    if (r.block === "I" || els.sort.value !== "order") meta.appendChild(el("span", "lit-tag", r.primary_category));
    if (r.publication_type === "Preprint") meta.appendChild(el("span", "lit-tag lit-tag-warn", "Preprint"));
    item.appendChild(meta);

    var date = cell(tr, "Fecha de lectura", "lit-col-date");
    date.textContent = r.reading_date || "—";
    if (!r.reading_date) date.classList.add("lit-empty");

    var link = cell(tr, "Artículo original", "lit-col-link");
    if (r.original_url) {
      var box = el("div", "lit-link-box");
      box.appendChild(extLink(r.original_url, "Ver artículo",
        "Abrir el artículo original en una pestaña nueva: " + r.title_original));
      if (r.doi) box.appendChild(el("span", "lit-doi", "DOI " + r.doi));
      link.appendChild(box);
    } else {
      link.appendChild(el("span", "lit-empty", "No disponible"));
    }

    var st = cell(tr, "Estado", "lit-col-status");
    var done = r.reading_status === "Realizado";
    var pill = el("span", "lit-pill " + (done ? "lit-pill-done" : "lit-pill-todo"));
    pill.appendChild(el("span", "lit-pill-icon", done ? "✓" : "○")).setAttribute("aria-hidden", "true");
    pill.appendChild(document.createTextNode(done ? "Realizado" : "Pendiente"));
    st.appendChild(pill);

    var lf = cell(tr, "Latent Frontiers", "lit-col-lf");
    if (r.latent_frontiers_url) {
      lf.appendChild(extLink(r.latent_frontiers_url, "Ver análisis",
        "Ver análisis en Latent Frontiers (pestaña nueva)"));
    } else {
      lf.textContent = "—";
      lf.classList.add("lit-empty");
    }
    return tr;
  }

  function render(resetPage) {
    if (resetPage) page = 0;
    var list = filtered();
    var pages = Math.max(1, Math.ceil(list.length / PAGE_SIZE));
    if (page >= pages) page = pages - 1;
    var start = page * PAGE_SIZE;
    var slice = list.slice(start, start + PAGE_SIZE);

    var frag = document.createDocumentFragment();
    var grouped = els.sort.value === "order";
    var prev = start > 0 ? groupKey(list[start - 1]) : null;
    slice.forEach(function (r, i) {
      if (grouped) {
        var k = groupKey(r);
        if (i === 0 || k !== prev) frag.appendChild(groupRow(r, i === 0 && k === prev));
        prev = k;
      }
      frag.appendChild(itemRow(r));
    });
    if (!slice.length) {
      var tr = el("tr", "lit-none");
      var td = el("td", null, "No hay referencias que coincidan con la búsqueda o los filtros.");
      td.colSpan = 6;
      tr.appendChild(td);
      frag.appendChild(tr);
    }
    els.tbody.replaceChildren(frag);

    els.count.textContent = list.length
      ? "Mostrando " + (start + 1) + "–" + (start + slice.length) + " de " +
        plural(list.length, "referencia", "referencias") +
        (list.length !== rows.length ? " (de " + rows.length + " en total)" : "")
      : "0 de " + rows.length + " referencias";

    renderPager(pages);
    syncChips();
  }

  function renderPager(pages) {
    els.pager.replaceChildren();
    if (pages <= 1) return;
    function btn(label, target, opts) {
      var b = el("button", "lit-page" + (opts && opts.current ? " is-current" : ""), label);
      b.type = "button";
      if (opts && opts.aria) b.setAttribute("aria-label", opts.aria);
      if (opts && opts.current) b.setAttribute("aria-current", "page");
      b.disabled = target < 0 || target >= pages || (opts && opts.current);
      b.addEventListener("click", function () {
        page = target;
        render(false);
        els.table.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      return b;
    }
    els.pager.appendChild(btn("‹ Anterior", page - 1, { aria: "Página anterior" }));
    for (var p = 0; p < pages; p++) {
      if (pages > 9 && p > 1 && p < pages - 2 && Math.abs(p - page) > 1) {
        if (!els.pager.lastChild.classList.contains("lit-gap")) els.pager.appendChild(el("span", "lit-gap", "…"));
        continue;
      }
      els.pager.appendChild(btn(String(p + 1), p, { current: p === page, aria: "Página " + (p + 1) }));
    }
    els.pager.appendChild(btn("Siguiente ›", page + 1, { aria: "Página siguiente" }));
  }

  // -------------------------------------------------------- navigation
  function chip(label, count, onClick, key) {
    var b = el("button", "lit-chip");
    b.type = "button";
    b.dataset.key = key;
    b.appendChild(el("span", null, label));
    b.appendChild(el("span", "lit-chip-count", String(count)));
    b.addEventListener("click", onClick);
    return b;
  }

  function buildChips() {
    var frag = document.createDocumentFragment();
    frag.appendChild(chip("Todo el catálogo", rows.length, function () { setFilters("", ""); }, "all"));
    frag.appendChild(chip("Anteproyecto doctoral", rows.filter(function (r) { return r.block === "I"; }).length,
      function () { setFilters("I", ""); }, "block:I"));
    categories.forEach(function (c) {
      var n = rows.filter(function (r) { return r.primary_category === c; }).length;
      frag.appendChild(chip(c, n, function () { setFilters("", c); }, "cat:" + c));
    });
    els.chips.replaceChildren(frag);
  }

  function syncChips() {
    var key = els.block.value === "I" && !els.cat.value ? "block:I"
      : (!els.block.value && els.cat.value ? "cat:" + els.cat.value
        : (!els.block.value && !els.cat.value ? "all" : ""));
    Array.prototype.forEach.call(els.chips.children, function (b) {
      var on = b.dataset.key === key;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  function setFilters(block, cat) {
    els.block.value = block;
    els.cat.value = cat;
    els.sort.value = "order";
    render(true);
    els.table.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // --------------------------------------------------------------- init
  function stats() {
    var set = function (k, v) {
      var n = document.querySelector('[data-stat="' + k + '"]');
      if (n) n.textContent = String(v);
    };
    set("total", rows.length);
    set("done", rows.filter(function (r) { return r.reading_status === "Realizado"; }).length);
    set("pending", rows.filter(function (r) { return r.reading_status !== "Realizado"; }).length);
    set("lf", rows.filter(function (r) { return !!r.latent_frontiers_url; }).length);
  }

  function init(data) {
    rows = data.map(function (r) {
      r._order = Number(r.reading_order) || 1e9;
      r._year = Number(r.publication_year) || 0;
      r._search = norm([r.title_original, r.title_es, r.authors, r.citation_short, r.doi, r.venue,
        r.primary_category, r.secondary_tags].join(" "));
      return r;
    }).sort(function (a, b) { return a._order - b._order; });

    rows.forEach(function (r) {
      if (r.block === "II" && categories.indexOf(r.primary_category) === -1) categories.push(r.primary_category);
    });
    rows.forEach(function (r) {
      if (categories.indexOf(r.primary_category) === -1) categories.push(r.primary_category);
    });
    categories.forEach(function (c) {
      var o = el("option", null, c);
      o.value = c;
      els.cat.appendChild(o);
    });

    stats();
    buildChips();

    var timer;
    els.q.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () { render(true); }, 150);
    });
    [els.block, els.cat, els.status, els.sort, els.lf].forEach(function (c) {
      c.addEventListener("change", function () { render(true); });
    });
    els.reset.addEventListener("click", function () {
      els.q.value = ""; els.block.value = ""; els.cat.value = ""; els.status.value = "";
      els.sort.value = "order"; els.lf.checked = false;
      render(true);
    });
    render(true);
  }

  fetch(CSV_URL, { cache: "no-cache" })
    .then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.text();
    })
    .then(function (text) { init(parseCSV(text)); })
    .catch(function (err) {
      els.count.textContent = "No se pudo cargar el catálogo (" + err.message + "). " +
        "Los datos están disponibles en data/literature_catalog.csv.";
    });
})();
