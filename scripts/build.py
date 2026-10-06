"""Gera o site dummy estático a partir de data/prestadores.json.

Saída (na raiz do repo):
  /<slug>.html                    página da busca com tags de prévia (Open Graph)
  /api/prestadores/<slug>.json    "API dummy" — simula GET /prestadores?categoria=<slug>
  /api/categorias.json            simula GET /categorias/
  /og/<slug>.png                  imagem do cartão de prévia (1200x630)
  /index.html, /404.html

Uso:
  INTER_FONT_DIR=/caminho/para/ttf python3 scripts/build.py
"""

from __future__ import annotations

import html
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_URL = os.environ.get("BASE_URL", "https://tgpmoraes.github.io/bemindicado-dummy")
ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = Path(os.environ.get("INTER_FONT_DIR", "/usr/share/fonts/truetype/dejavu"))

GREEN = "#1f6e47"
SOFT = "#e3f4ea"


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    names = {"bold": ["Inter-Bold.ttf", "DejaVuSans-Bold.ttf"],
             "semi": ["Inter-SemiBold.ttf", "DejaVuSans-Bold.ttf"],
             "regular": ["Inter-Regular.ttf", "DejaVuSans.ttf"]}[weight]
    for n in names:
        p = FONT_DIR / n
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


def avaliados(cat: dict) -> int:
    return sum(1 for p in cat["prestadores"] if p["nota"] is not None)


def og_image(cat: dict, condominio: str, out: Path) -> None:
    img = Image.new("RGB", (1200, 630), GREEN)
    d = ImageDraw.Draw(img)
    # marca
    d.rounded_rectangle((80, 72, 136, 128), radius=14, fill="white")
    d.text((108, 100), "BI", font=font("bold", 24), fill=GREEN, anchor="mm")
    d.text((156, 100), "Bem Indicado", font=font("semi", 34), fill="white", anchor="lm")
    # título
    d.text((80, 300), cat["plural"], font=font("bold", 118), fill="white", anchor="ls")
    d.text((80, 380), f"indicados no {condominio}", font=font("semi", 46), fill=SOFT, anchor="ls")
    # rodapé
    n = avaliados(cat)
    pill = f"{n} avaliados pelos vizinhos" if n != 1 else "1 avaliado pelos vizinhos"
    f = font("semi", 32)
    w = d.textlength(pill, font=f)
    d.rounded_rectangle((80, 470, 80 + w + 56, 534), radius=32, fill=SOFT)
    d.text((108, 502), pill, font=f, fill=GREEN, anchor="lm")
    img.save(out, "PNG", optimize=True)


PAGE = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Bem Indicado">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2c8a5b">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}style.css">
</head>
<body data-slug="{slug}" data-rel="{rel}">
<header class="top"><a href="{rel}" class="brand"><span class="mark">BI</span>Bem Indicado</a><span class="tag">teste</span></header>
<main class="wrap">
<h1>Buscar prestadores</h1>
<div class="search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg><span id="termo">{termo}</span></div>
<div class="chips"><span class="chip on">Categoria: {termo}</span><span class="chip">{condominio}</span></div>
<p class="api">API dummy: <code id="api"></code></p>
<div id="out"><p class="muted">Carregando…</p></div>
<p class="foot">Página de teste · prestadores fictícios</p>
</main>
<script src="{rel}app.js"></script>
</body>
</html>
"""


def page(cat: dict, condominio: str) -> str:
    n = avaliados(cat)
    title = f"{cat['plural']} indicados no {condominio}"
    desc = (f"{n} prestadores avaliados pelos vizinhos. Toque para ver." if n != 1
            else "1 prestador avaliado pelos vizinhos. Toque para ver.")
    esc = html.escape
    return PAGE.format(
        title=esc(title), desc=esc(desc), url=f"{BASE_URL}/{cat['slug']}",
        image=f"{BASE_URL}/og/{cat['slug']}.png", rel="./", slug=cat["slug"],
        termo=esc(cat["nome"]), condominio=esc(condominio),
    )


INDEX = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bem Indicado — teste de links</title>
<meta property="og:title" content="Bem Indicado — indicações dos vizinhos">
<meta property="og:description" content="Digite o link + o serviço. Ex.: /encanador">
<meta property="og:image" content="{base}/og/encanador.png">
<meta property="og:url" content="{base}/">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="./style.css">
</head>
<body>
<header class="top"><a href="./" class="brand"><span class="mark">BI</span>Bem Indicado</a><span class="tag">teste</span></header>
<main class="wrap">
<h1>Indicações dos vizinhos</h1>
<p class="muted">Cole no WhatsApp o link + o serviço. Categorias deste teste:</p>
<ul class="cats">
{items}
</ul>
<p class="foot">Página de teste · prestadores fictícios</p>
</main>
</body>
</html>
"""

NOT_FOUND = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bem Indicado — busca</title>
<meta property="og:title" content="Buscar prestadores — Bem Indicado">
<meta property="og:description" content="Veja quem os vizinhos do Colinas do Paratehy indicam.">
<meta property="og:image" content="https://tgpmoraes.github.io/bemindicado-dummy/og/encanador.png">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/bemindicado-dummy/style.css">
</head>
<body>
<header class="top"><a href="/bemindicado-dummy/" class="brand"><span class="mark">BI</span>Bem Indicado</a><span class="tag">teste</span></header>
<main class="wrap">
<h1>Buscar prestadores</h1>
<div class="search"><span id="termo"></span></div>
<div class="empty">Nenhum prestador encontrado para “<span id="t2"></span>”.<br>Se você conhece um, cadastre e ajude os vizinhos.</div>
<p class="muted"><a href="/bemindicado-dummy/">Ver categorias disponíveis</a></p>
</main>
<script>
var t = decodeURIComponent(location.pathname.replace(/^\\/bemindicado-dummy\\//, "").replace(/\\/$/, "")).replace(/-/g, " ");
document.getElementById("termo").textContent = t;
document.getElementById("t2").textContent = t;
</script>
</body>
</html>
"""


def main() -> None:
    data = json.loads((ROOT / "data" / "prestadores.json").read_text(encoding="utf-8"))
    condominio: str = data["condominio"]
    (ROOT / "og").mkdir(exist_ok=True)
    (ROOT / "api" / "prestadores").mkdir(parents=True, exist_ok=True)

    cats_api = []
    items = []
    for cat in data["categorias"]:
        slug = cat["slug"]
        # arquivo plano <slug>.html: o GitHub Pages serve /<slug> sem redirecionar
        # (pasta <slug>/ gera um 301 para /<slug>/, e o WhatsApp não monta a prévia)
        (ROOT / f"{slug}.html").write_text(page(cat, condominio), encoding="utf-8")
        api = {"categoria": {"slug": slug, "nome": cat["nome"]}, "condominio": condominio,
               "total": len(cat["prestadores"]), "prestadores": cat["prestadores"]}
        (ROOT / "api" / "prestadores" / f"{slug}.json").write_text(
            json.dumps(api, ensure_ascii=False, indent=2), encoding="utf-8")
        og_image(cat, condominio, ROOT / "og" / f"{slug}.png")
        cats_api.append({"slug": slug, "nome": cat["nome"]})
        items.append(f'<li><a href="./{slug}">{html.escape(cat["nome"])}</a>'
                     f'<code>/{slug}</code></li>')

    (ROOT / "api" / "categorias.json").write_text(
        json.dumps(cats_api, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "index.html").write_text(INDEX.format(base=BASE_URL, items="\n".join(items)), encoding="utf-8")
    (ROOT / "404.html").write_text(NOT_FOUND, encoding="utf-8")
    print(f"ok: {len(cats_api)} categorias")


if __name__ == "__main__":
    main()
