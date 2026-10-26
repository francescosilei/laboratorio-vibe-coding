"""Legge un PDF con più ricette (una per pagina) e prepara il materiale per l'importazione.

  python3 tools/pdf_ricette.py estrai FILE.pdf [FILE2.pdf ...] --out CARTELLA [--foto-box x0,y0,x1,y1]

Una ricetta = un file PDF (le sue pagine sono fette consecutive dello screenshot e vengono riunite), oppure
un segnalibro di un PDF combinato. Per ogni ricetta scrive in CARTELLA/<codice>/:
  testo.txt   testa (titolo, tempi, porzioni), ingredienti e preparazione, già divisi per colonna
  foto.jpg    foto della ricetta, ritagliata dalla pagina
  pagina.png  screenshot intero a piena risoluzione (solo per controlli puntuali)
e in CARTELLA/indice.txt un rigo per ricetta (codice Cookidoo, dimensioni, righe incerte).

Legge SEMPRE l'immagine a piena risoluzione con RapidOCR e ignora l'eventuale testo selezionabile aggiunto da
Acrobat: provato su 5 PDF, quel testo è pieno di errori («l5 min./100?C»), con colonne mescolate e cifre perse. Layout previsto: schede Cookidoo
(ingredienti a sinistra, preparazione a destra). Per altri layout serve adattare le costanti qui sotto.

Nel testo OCR le icone di Cookidoo non sono lette, ma lasciano un segno:
  «/ /vel.»  (doppia barra)  rotazione antioraria      «vel. .»  o  «vel. s»   velocità cucchiaio
"""
import argparse, json, pathlib, re, shutil, subprocess, sys, tempfile

COL_SX_FINE, COL_DX_INIZIO, TESTA_FINE = 0.47, 0.45, 0.20    # frazioni di larghezza/altezza della pagina
FOTO = (0.186, 154, 0.491, 633)                               # x0, y0, x1 (frazioni), y1 in pixel a 1910 px di larghezza
STOP_SX = ("Dispositivi", "Articoli utili")
STOP_DX = ("Condividi ricetta", "Le mie note")


def correggi(t):
    """errori tipici dell'OCR sulle cifre: 1oo -> 100, 3o -> 30, 1oo'c -> 100°C"""
    t = re.sub(r"(?<=\d)[oO](?=\d|\b)", "0", t)
    t = re.sub(r"\b[oO](?=\d)", "0", t)
    t = re.sub(r"(?<=\d)['`]c\b", "°C", t)
    return t.replace("°c", "°C").replace("I'", "l'")


def righe(boxes, tol=14):
    out, cur, cy = [], [], None
    for b in sorted(boxes, key=lambda b: ((b["y0"] + b["y1"]) / 2, b["x0"])):
        c = (b["y0"] + b["y1"]) / 2
        if cy is None or abs(c - cy) <= tol:
            cur.append(b); cy = c if cy is None else (cy + c) / 2
        else:
            out.append(cur); cur = [b]; cy = c
    if cur: out.append(cur)
    return [(" ".join(b["t"] for b in sorted(r, key=lambda b: b["x0"])), min(b["c"] for b in r)) for r in out]


def colonne(boxes, w, h):
    testa = [b for b in boxes if b["x0"] > w * COL_DX_INIZIO and b["y0"] < h * TESTA_FINE]
    sx = [b for b in boxes if b["x1"] < w * COL_SX_FINE and b["y0"] >= h * TESTA_FINE]
    dx = [b for b in boxes if b["x0"] >= w * COL_DX_INIZIO and b["y0"] >= h * TESTA_FINE]
    def fino_a(col, stop):
        res = []
        for t, c in righe(col):
            if any(s in t for s in stop): break
            res.append((t, c))
        return res
    return righe(testa), fino_a(sx, STOP_SX), fino_a(dx, STOP_DX)


def formatta(testa, ing, prep):
    ruido = ("bimby", "VORWERK", "settimana", "Oggi cucino", "valutazioni", "Per Te", "Esplora")
    def riga(t, c): return correggi(t) + (f"   [?{c:.2f}]" if c < .8 else "")
    L = ["## TESTA"] + [correggi(t) for t, _ in testa if not any(k in t for k in ruido)]
    L += ["", "## INGREDIENTI"] + [riga(t, c) for t, c in ing if not t.startswith(("Porzioni", "+ Adatta", "Ingredienti"))]
    L += ["", "## PREPARAZIONE"] + [riga(t, c) for t, c in prep if not t.startswith("Preparazione")]
    return "\n".join(L) + "\n"


def gruppi(reader):
    """pagine per ricetta: dai segnalibri se ci sono, altrimenti tutto il file è una sola ricetta"""
    n = len(reader.pages)
    voci = []
    for o in reader.outline or []:
        if hasattr(o, "title"):
            try: voci.append((reader.get_destination_page_number(o), o.title))
            except Exception: pass
    if len(voci) < 2:
        return [(None, list(range(n)))]
    voci.sort()
    fine = [v[0] for v in voci[1:]] + [n]
    return [(t, list(range(a, b))) for (a, t), b in zip(voci, fine)]


def estrai(a):
    import numpy as np
    from PIL import Image
    from pypdf import PdfReader
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ocr = None
    indice = []
    for pdf in map(pathlib.Path, a.pdf):
        reader = PdfReader(str(pdf))
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["pdfimages", "-png", "-p", str(pdf), f"{tmp}/p"], check=True)
            per_pagina = {}
            for f in sorted(pathlib.Path(tmp).glob("p-*.png")):
                per_pagina.setdefault(int(f.name.split("-")[1]) - 1, []).append(f)
            for titolo, pagine in gruppi(reader):
                nome = titolo or pdf.stem
                cod = re.search(r"-(r\d+)-", nome)
                rid = cod.group(1) if cod else re.sub(r"\W+", "-", nome)[:40]
                fogli = [Image.open(f).convert("RGB") for pg in pagine for f in per_pagina.get(pg, [])]
                if not fogli:
                    indice.append(f"{rid}  SALTATA: nessuna immagine nelle pagine {pagine[0] + 1}-{pagine[-1] + 1}"); continue
                w = fogli[0].width
                im = Image.new("RGB", (w, sum(f.height for f in fogli)), "white"); y = 0
                for f in fogli: im.paste(f, (0, y)); y += f.height      # le pagine sono fette consecutive dello screenshot
                h = im.height
                d = out / rid; d.mkdir(exist_ok=True)
                im.save(d / "pagina.png")
                if ocr is None:
                    from rapidocr_onnxruntime import RapidOCR
                    ocr = RapidOCR()
                res, _ = ocr(np.array(im))
                boxes = [{"x0": min(p[0] for p in bx), "y0": min(p[1] for p in bx), "x1": max(p[0] for p in bx),
                          "y1": max(p[1] for p in bx), "t": t, "c": float(c)} for bx, t, c in (res or [])]
                testa, ing, prep = colonne(boxes, w, h)
                (d / "testo.txt").write_text(formatta(testa, ing, prep), encoding="utf-8")
                if a.foto_box:
                    box = tuple(int(x) for x in a.foto_box.split(","))
                else:
                    sc = w / 1910
                    box = (int(FOTO[0] * w), int(FOTO[1] * sc), int(FOTO[2] * w), int(FOTO[3] * sc))
                foto = im.crop(box)
                if foto.width > 800: foto = foto.resize((800, round(foto.height * 800 / foto.width)), Image.LANCZOS)
                foto.save(d / "foto.jpg", quality=86, optimize=True)
                dubbi = sum(1 for _, c in ing + prep if c < .8)
                indice.append(f"{rid}  origine=cookidoo:{rid}  {w}x{h}  pagine={len(fogli)}  righe_incerte={dubbi}")
    (out / "indice.txt").write_text("\n".join(indice) + "\n", encoding="utf-8")
    print("\n".join(indice))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("estrai"); p.add_argument("pdf", nargs="+"); p.add_argument("--out", required=True); p.add_argument("--foto-box")
    a = ap.parse_args()
    estrai(a)


if __name__ == "__main__":
    main()
