"""Compone dist/index.html (frammento da pubblicare) e dist/preview.html (pagina completa per prove locali)."""
import base64, json, pathlib
root = pathlib.Path(__file__).resolve().parent
ricette = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((root / "data" / "ricette").glob("*.json"))]
ricette.sort(key=lambda r: r["titolo"].lower())
ricette.sort(key=lambda r: r.get("importata", ""), reverse=True)   # le ultime importate in cima
dati = json.dumps(ricette, ensure_ascii=False)
img = {f.name: "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()
       for f in sorted((root / "data" / "img").glob("*.jpg"))}
html = (root / "app" / "template.html").read_text(encoding="utf-8")
html = html.replace("__DATA__", dati.replace("</", "<\\/")).replace("__IMG__", json.dumps(img))
out = root / "dist"; out.mkdir(exist_ok=True)
(out / "index.html").write_text(html, encoding="utf-8")
wrap = ('<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<style>:root{color-scheme:light}body{margin:0;font:14px system-ui}[hidden]{display:none!important}img{max-width:100%}</style></head><body>'
        + html + "</body></html>")
(out / "preview.html").write_text(wrap, encoding="utf-8")
print(f"dist/index.html {len(html)//1024} KB")
