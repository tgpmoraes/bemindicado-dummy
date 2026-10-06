// Simula a chamada GET /prestadores?categoria=<slug> lendo o JSON estático da "API dummy".
(function () {
  var slug = document.body.dataset.slug;
  var rel = document.body.dataset.rel || "./";
  var url = rel + "api/prestadores/" + slug + ".json";
  document.getElementById("api").textContent = "GET /api/prestadores/" + slug + ".json";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function fmtTel(e164) {
    var d = e164.replace(/\D/g, "").replace(/^55/, "");
    return "(" + d.slice(0, 2) + ") " + d.slice(2, 7) + "-" + d.slice(7);
  }
  function card(p, cat) {
    var right = p.nota != null
      ? '<div class="nota"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></svg>' +
        p.nota.toFixed(1).replace(".", ",") + '</div><div class="small">' + p.avaliacoes + ' aval.</div><div class="pct">' + p.recomendam_pct + '% recomendam</div>'
      : '<div class="small">Sem avaliações</div>';
    var hint = p.nota == null ? '<div class="hint">Se você já contratou esse prestador, seja o primeiro a avaliar no seu condomínio.</div>' : "";
    return '<article class="card"><div class="row"><div class="info"><h3>' + esc(p.nome) + '</h3><div class="small">' + esc(cat) +
      '</div><p>' + esc(p.descricao) + '</p><a class="wa" href="https://wa.me/' + p.telefone.replace(/\D/g, "") + '">' + fmtTel(p.telefone) +
      '</a></div><div class="side">' + right + '</div></div>' + hint + '</article>';
  }
  function section(title, sub, list, cat) {
    if (!list.length) return "";
    return '<section><h2>' + title + '</h2><p class="small">' + sub + '</p>' + list.map(function (p) { return card(p, cat); }).join("") + '</section>';
  }

  fetch(url)
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (res) {
      var ps = res.prestadores || [];
      var ind = ps.filter(function (p) { return p.nota != null; }).sort(function (a, b) { return b.nota - a.nota; });
      var out = ps.filter(function (p) { return p.nota == null; });
      var nome = res.categoria.nome;
      document.getElementById("out").innerHTML = ps.length
        ? section("Indicados no seu condomínio", "Já avaliados por moradores do seu condomínio.", ind, nome) +
          section("Outros prestadores cadastrados", "Ainda sem avaliação no seu condomínio.", out, nome)
        : '<div class="empty">Nenhum prestador encontrado.</div>';
    })
    .catch(function () {
      document.getElementById("out").innerHTML = '<div class="empty">Não foi possível carregar os prestadores agora.</div>';
    });
})();
