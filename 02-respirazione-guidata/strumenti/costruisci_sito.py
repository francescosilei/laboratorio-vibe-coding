#!/usr/bin/env python3
"""Costruisce la cartella `sito/` a partire dall'app (02-respirazione-guidata/index.html).

Uso:  python3 02-respirazione-guidata/strumenti/costruisci_sito.py [--og-base=https://utente.github.io/nome-repo/]   (indirizzo «principale»: anteprima di WhatsApp e indirizzo canonico per i motori di ricerca)

Cosa fa:
- trasforma la pagina in un documento autonomo (doctype, meta, icone, manifest, font locali);
- toglie l'audio incorporato (dati base64) e lo sostituisce con file in sito/audio/;
- sostituisce il logo incorporato con il file sito/immagini/logo-spirale.webp;
- scrive i file di supporto (manifest, 404, robots, _headers, netlify.toml, .nojekyll).
Tutti i percorsi sono relativi, così il sito funziona sia alla radice (Netlify) sia in una sottocartella (GitHub Pages).
"""
import json, os, re, shutil, sys

RADICE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SORGENTE = os.path.join(RADICE, "02-respirazione-guidata", "index.html")
AUDIO = os.path.join(RADICE, "02-respirazione-guidata", "audio", "chiara")
SITO = os.path.join(RADICE, "sito")
OG_BASE = ""
for a in sys.argv[1:]:
    if a.startswith("--og-base="):
        OG_BASE = a.split("=", 1)[1].rstrip("/") + "/"

# chiave usata dall'app -> nome del file registrato
def file_audio(chiave):
    if chiave in ("inspira", "trattieni", "espira"):
        return "respira_cue_%s_b.mp3" % chiave
    if chiave.startswith(("presente_", "sonno_", "gentilezza_")):
        return chiave + ".mp3"
    return "respira_" + chiave + ".mp3"          # benvenuto, intro_*, chiusura, accompagna_NN

src = open(SORGENTE, encoding="utf-8").read()

# 1) audio: da dati incorporati a file
chiavi = []
def sostituisci(m):
    chiavi.append(m.group(2))
    return "%s%s%s: 'audio/%s.mp3'" % (m.group(1), m.group(2), m.group(1), m.group(2))
src, n = re.subn(r"(['\"]?)(\w+)\1: 'data:audio/mpeg;base64,[A-Za-z0-9+/=]+'", sostituisci, src)
os.makedirs(os.path.join(SITO, "audio"), exist_ok=True)
for f in os.listdir(os.path.join(SITO, "audio")):
    os.remove(os.path.join(SITO, "audio", f))
mancanti = []
for k in chiavi:
    origine = os.path.join(AUDIO, file_audio(k))
    if not os.path.exists(origine):
        mancanti.append(k); continue
    shutil.copy(origine, os.path.join(SITO, "audio", k + ".mp3"))
if mancanti:
    sys.exit("File audio mancanti: " + ", ".join(mancanti))

# 2) logo: da dati incorporati a file
src, n_logo = re.subn(r'src="data:image/webp;base64,[A-Za-z0-9+/=]+"', 'src="immagini/logo-spirale.webp"', src)
assert n_logo == 1, "logo non trovato"

# 3) indirizzo di condivisione: quello della pagina, qualunque sia il sito
src, n_url = re.subn(r"var URL_PAGE = '[^']*';", "var URL_PAGE = location.href.split('#')[0].split('?')[0];", src)
assert n_url == 1, "URL_PAGE non trovato"

# 4) separa <title>, meta e caratteri esterni dal resto
src = re.sub(r"<title>.*?</title>\n?", "", src, count=1)
src = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", src, count=1)
src = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n?', "", src, count=1)
m = re.search(r"<style>(.*?)</style>", src, re.S)
css_app, corpo = m.group(1), (src[:m.start()] + src[m.end():]).strip()

TITOLO = "Un momento per te"
DESCR = "Piccoli strumenti per fermarti, respirare e ritrovare il tuo spazio, a cura della Dott.ssa Maria Chiara D'Iorio, psicologa. Senza account e senza raccolta di dati."
og = ""
canon = ""
if OG_BASE:
    canon = '<link rel="canonical" href="%s">\n' % OG_BASE
    og = ('<meta property="og:type" content="website">\n<meta property="og:locale" content="it_IT">\n'
          '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n'
          '<meta property="og:url" content="%s">\n'
          '<meta property="og:image" content="%sicons/og-image.png">\n<meta name="twitter:card" content="summary_large_image">\n' % (TITOLO, DESCR, OG_BASE, OG_BASE))

head = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>%(t)s</title>
<meta name="description" content="%(d)s">
%(canon)s<meta name="theme-color" content="#f5f3e9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#16241c" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
%(og)s<style>
:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
html{scroll-padding-top:env(safe-area-inset-top,0px)}
body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#fff;color:#000}
img{max-width:100%%}
[hidden]:not([hidden=until-found i]){display:none!important}
@font-face{font-family:"Nunito Sans";font-style:normal;font-weight:400 700;font-display:swap;src:url(fonts/nunito-sans-latin.woff2) format("woff2")}
</style>
<style>%(css)s</style>
</head>
<body>
%(corpo)s
</body>
</html>
""" % {"t": TITOLO, "d": DESCR, "og": og, "canon": canon, "css": css_app, "corpo": corpo}
open(os.path.join(SITO, "index.html"), "w", encoding="utf-8").write(head)

# 5) file di supporto
manifest = {
    "name": TITOLO, "short_name": "Un momento", "description": DESCR, "lang": "it",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": "#f5f3e9", "theme_color": "#f5f3e9",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
open(os.path.join(SITO, "manifest.webmanifest"), "w").write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
open(os.path.join(SITO, "404.html"), "w", encoding="utf-8").write("""<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pagina non trovata</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f5f3e9;color:#263d32;font:18px/1.55 system-ui,sans-serif;padding:24px;text-align:center}
a{color:#526d58;font-weight:700}h1{font:700 2rem Georgia,serif;margin:0 0 12px}</style></head>
<body><main><h1>Pagina non trovata</h1><p>Questa pagina non esiste.</p><p><a href="./">Torna a «Un momento per te»</a></p></main></body></html>
""")
open(os.path.join(SITO, "robots.txt"), "w").write("User-agent: *\nAllow: /\n")        # il sito può comparire sui motori di ricerca
open(os.path.join(SITO, ".nojekyll"), "w").write("")
open(os.path.join(SITO, "_headers"), "w").write("""/audio/*
  Cache-Control: public, max-age=86400
/icons/*
  Cache-Control: public, max-age=604800
/immagini/*
  Cache-Control: public, max-age=604800
/fonts/*
  Cache-Control: public, max-age=31536000, immutable
""")
open(os.path.join(SITO, "netlify.toml"), "w").write('[build]\n  publish = "."\n')
open(os.path.join(SITO, "fonts", "LICENZA-Nunito-Sans.txt"), "w", encoding="utf-8").write(
    "Nunito Sans: Copyright 2016 The Nunito Project Authors. Licenza SIL Open Font License 1.1 (https://openfontlicense.org).\n")
open(os.path.join(SITO, "README.md"), "w", encoding="utf-8").write(
    "# Un momento per te\n\nSito statico: piccoli strumenti per fermarsi, respirare e ritrovare il proprio spazio.\nNon usa account, cookie o servizi esterni e non raccoglie dati.\n")
tot = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(SITO) for f in fs)
print("Pagina: %.0f KB | clip audio: %d | totale sito: %.1f MB" % (os.path.getsize(os.path.join(SITO, "index.html")) / 1024, len(chiavi), tot / 1e6))
