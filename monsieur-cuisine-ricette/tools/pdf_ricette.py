"""Legge un PDF con più ricette (una per pagina) e prepara il materiale per l'importazione.

  python3 tools/pdf_ricette.py estrai FILE.pdf --out CARTELLA [--foto-box x0,y0,x1,y1]

Per ogni pagina scrive in CARTELLA:
  NN-testo.txt   testa (titolo, tempi, porzioni), ingredienti e preparazione, già divisi per colonna
  NN-foto.jpg    foto della ricetta, ritagliata dalla pagina
  NN-pagina.png  pagina intera a piena risoluzione (solo per controlli puntuali)
  indice.txt     un rigo per pagina: titolo del segnalibro, codice Cookidoo, righe incerte

Funziona sui PDF «immagine» (screenshot): estrae lo screenshot a piena risoluzione e ne legge il testo con
RapidOCR. Se la pagina ha già il testo selezionabile, usa quello. Layout previsto: schede Cookidoo
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


def estrai(a):
    import numpy as np
    from PIL import Image
    from pypdf import PdfReader
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    pdf = pathlib.Path(a.pdf)
    reader = PdfReader(str(pdf))
    nomi = [o.title for o in reader.outline if hasattr(o, "title")] if reader.outline else []
    n = len(reader.pages)
    ocr = None
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdfimages", "-png", str(pdf), f"{tmp}/p"], check=True)
        imgs = sorted(pathlib.Path(tmp).glob("p-*.png"))
        if len(imgs) < n:
            sys.exit(f"{len(imgs)} immagini per {n} pagine: il PDF non è di sole immagini a pagina intera. "
                     "Serve adattare lo strumento (testo selezionabile? pagine divise?).")
        indice = []
        for i in range(n):
            nn = f"{i + 1:02d}"
            shutil.copy(imgs[i], out / f"{nn}-pagina.png")
            im = Image.open(imgs[i]).convert("RGB"); w, h = im.size
            if ocr is None:
                from rapidocr_onnxruntime import RapidOCR
                ocr = RapidOCR()
            res, _ = ocr(np.array(im))
            boxes = [{"x0": min(p[0] for p in bx), "y0": min(p[1] for p in bx), "x1": max(p[0] for p in bx),
                      "y1": max(p[1] for p in bx), "t": t, "c": float(c)} for bx, t, c in (res or [])]
            testa, ing, prep = colonne(boxes, w, h)
            (out / f"{nn}-testo.txt").write_text(formatta(testa, ing, prep), encoding="utf-8")
            if a.foto_box:
                box = tuple(int(x) for x in a.foto_box.split(","))
            else:
                s = w / 1910
                box = (int(FOTO[0] * w), int(FOTO[1] * s), int(FOTO[2] * w), int(FOTO[3] * s))
            foto = im.crop(box)
            if foto.width > 800: foto = foto.resize((800, round(foto.height * 800 / foto.width)), Image.LANCZOS)
            foto.save(out / f"{nn}-foto.jpg", quality=86, optimize=True)
            nome = nomi[i] if i < len(nomi) else f"pagina {i + 1}"
            cod = re.search(r"-(r\d+)-", nome)
            dubbi = sum(1 for _, c in ing + prep if c < .8)
            indice.append(f"{nn}  {nome}  origine=cookidoo:{cod.group(1) if cod else '?'}  {w}x{h}  righe_incerte={dubbi}")
    (out / "indice.txt").write_text("\n".join(indice) + "\n", encoding="utf-8")
    print("\n".join(indice))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("estrai"); p.add_argument("pdf"); p.add_argument("--out", required=True); p.add_argument("--foto-box")
    a = ap.parse_args()
    estrai(a)


if __name__ == "__main__":
    main()
