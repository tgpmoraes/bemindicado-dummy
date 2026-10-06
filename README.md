# bemindicado-dummy

Site estático de teste para validar a busca por link no grupo de WhatsApp do condomínio:
o morador cola `…/encanador` no grupo, o WhatsApp mostra o cartão de prévia e o toque abre a busca filtrada.

Todos os prestadores são **fictícios**.

- `data/prestadores.json` — dados de entrada
- `api/prestadores/<slug>.json` — "API dummy" (simula `GET /prestadores?categoria=<slug>`)
- `<slug>.html` — página com tags Open Graph (título, descrição, imagem)
- `og/<slug>.png` — imagem do cartão (1200×630)

Regerar após editar os dados:

```bash
INTER_FONT_DIR=/caminho/para/Inter/ttf python3 scripts/build.py
```

Publicado via GitHub Pages: https://tgpmoraes.github.io/bemindicado-dummy/
