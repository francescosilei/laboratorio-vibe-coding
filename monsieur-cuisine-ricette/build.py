"""Compone dist/index.html (frammento da pubblicare) e dist/preview.html (pagina completa per prove locali)."""
import base64, json, pathlib, sys
root = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(root / "tools"))
import spesa
ricette = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((root / "data" / "ricette").glob("*.json"))]
for r in ricette: r["spesa"] = spesa.spesa_ricetta(r)   # voci della lista della spesa (nome unico, quantità, unità, reparto)
ricette.sort(key=lambda r: r["titolo"].lower())
ricette.sort(key=lambda r: r.get("importata", ""), reverse=True)   # le ultime importate in cima
dati = json.dumps(ricette, ensure_ascii=False)
img = {f.name: "data:image/jpeg;base64," + base64.b64encode(f.read_bytes()).decode()
       for f in sorted((root / "data" / "img").glob("*.jpg"))}
html = (root / "app" / "template.html").read_text(encoding="utf-8")
logo = "data:image/webp;base64," + base64.b64encode((root / "app" / "logo.webp").read_bytes()).decode()   # logo Tommy Gourmet
html = html.replace("__LOGO__", logo).replace("__REGOLE__", json.dumps(spesa.regole(), ensure_ascii=False)).replace("__DATA__", dati.replace("</", "<\\/")).replace("__IMG__", json.dumps(img))
out = root / "dist"; out.mkdir(exist_ok=True)
(out / "index.html").write_text(html, encoding="utf-8")
wrap = ('<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<link rel="manifest" href="manifest.webmanifest"><link rel="icon" type="image/png" href="icon-192.png"><link rel="apple-touch-icon" href="apple-touch-icon.png">'
        '<meta name="theme-color" content="#f97316"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="default"><meta name="apple-mobile-web-app-title" content="Tommy Gourmet">'
        '<style>:root{color-scheme:light}body{margin:0;font:14px system-ui}[hidden]{display:none!important}img{max-width:100%}</style></head><body>'
        + html + "</body></html>")
(out / "preview.html").write_text(wrap, encoding="utf-8")
import shutil
for f in (root / "app" / "pwa").iterdir(): shutil.copy(f, out / f.name)   # icona e manifest per l'installazione sul telefono
print(f"dist/index.html {len(html)//1024} KB")
