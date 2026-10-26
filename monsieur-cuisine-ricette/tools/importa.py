"""Meccanica dell'importazione delle ricette (la lettura degli screenshot la fa Claude).

  python3 tools/importa.py stato
      elenca gli screenshot in import/inbox/ e segnala quelli poco leggibili

  python3 tools/importa.py aggiungi ricetta.json --screenshot a.png b.png [--foto a.png --crop x0,y0,x1,y1]
      controlla la ricetta; se non ci sono errori la aggiunge a data/ricette/, ritaglia la foto,
      sposta gli screenshot in import/ok/<id>/ e ricostruisce l'app. Se ci sono errori non cambia nulla.

  python3 tools/importa.py fallita nome "motivo" a.png b.png
      sposta gli screenshot in import/failed/<nome>/ con un file motivo.txt
"""
import argparse, datetime, json, pathlib, shutil, subprocess, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import valida

ROOT = valida.ROOT
INBOX, OK, FAILED = (ROOT / "import" / d for d in ("inbox", "ok", "failed"))
IMG = ROOT / "data" / "img"
SALTA = {".gitkeep", "README.md"}


def percorso(nome):
    p = pathlib.Path(nome)
    if p.exists():
        return p
    if (INBOX / nome).exists():
        return INBOX / nome
    sys.exit(f"file non trovato: {nome}")


def sposta(files, dest):
    dest.mkdir(parents=True, exist_ok=True)
    for n, f in enumerate(files, 1):
        shutil.move(str(f), dest / f"{dest.name}-{n}{f.suffix.lower()}")


def stato():
    from PIL import Image
    files = sorted(f for f in INBOX.iterdir() if f.is_file() and f.name not in SALTA)
    print(f"inbox: {len(files)} file")
    for f in files:
        try:
            w, h = Image.open(f).size
            note = []
            if w < 700: note.append("bassa risoluzione")
            if h / w > 2.5: note.append("pagina molto lunga: il testo può risultare piccolo, meglio ritagliare la scheda")
            print(f"  {f.name}  {w}x{h}" + (f"  [{'; '.join(note)}]" if note else ""))
        except Exception:
            print(f"  {f.name}  (non è un'immagine: ignorato)")
    ok = [d for d in OK.iterdir() if d.is_dir()]
    ko = [d for d in FAILED.iterdir() if d.is_dir()]
    print(f"ok: {len(ok)} ricette importate   failed: {len(ko)}")
    for d in ko:
        m = d / "motivo.txt"
        print(f"  failed/{d.name}: {m.read_text().splitlines()[-1] if m.exists() else '?'}")


def aggiungi(a):
    from PIL import Image
    try:
        r = json.loads(pathlib.Path(a.ricetta).read_text(encoding="utf-8"))
    except Exception as e:
        sys.exit(f"JSON non leggibile: {e}")
    esistenti = valida.carica_tutte()
    prova = dict(r, immagine=None) if a.foto else r
    E, W = valida.valida(prova, esistenti)
    if a.foto:
        W = [w for w in W if w != "nessuna foto"]
    if E:
        print("NON IMPORTATA, errori:")
        for e in E: print("  ERRORE ", e)
        for w in W: print("  avviso ", w)
        return 1

    rid = r["id"]
    if a.foto:
        im = Image.open(percorso(a.foto)).convert("RGB")
        if a.crop:
            im = im.crop(tuple(int(x) for x in a.crop.split(",")))
        if im.width < 600:                       # anteprime piccole: raddoppia per un risultato più morbido
            im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
        if im.width > 800:
            im = im.resize((800, round(im.height * 800 / im.width)), Image.LANCZOS)
        im.save(IMG / f"{rid}.jpg", quality=86, optimize=True)
        r["immagine"] = f"{rid}.jpg"
    r.setdefault("importata", datetime.date.today().isoformat())
    (ROOT / "data" / "ricette" / f"{rid}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")

    files = [percorso(n) for n in a.screenshot]
    if a.foto and percorso(a.foto) not in files and percorso(a.foto).parent == INBOX:
        files.append(percorso(a.foto))
    sposta(files, OK / rid)
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)

    avv = [(n, p["avvertenza"]) for n, p in enumerate(r["passi"], 1) if p.get("avvertenza")]
    na = [k for k in ("categoria", "paese", "difficolta") if r.get(k) == "NA"] + [k for k in ("tempo_min", "porzioni") if r.get(k) is None]
    print(f"IMPORTATA: {r['titolo']} ({len(r['passi'])} passi) -> import/ok/{rid}/")
    if r.get("dedotto"): print("  dedotti:", ", ".join(r["dedotto"]))
    if na: print("  NA:", ", ".join(na))
    for n, t in avv: print(f"  da valutare, passo {n}: {t}")
    for w in W: print("  avviso ", w)
    return 0


def fallita(a):
    files = [percorso(n) for n in a.file]
    dest = FAILED / a.nome
    sposta(files, dest)
    (dest / "motivo.txt").write_text(f"{datetime.date.today().isoformat()}\n{a.motivo}\n", encoding="utf-8")
    print(f"spostati {len(files)} file in import/failed/{a.nome}/  ({a.motivo})")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("stato")
    p = sub.add_parser("aggiungi"); p.add_argument("ricetta"); p.add_argument("--screenshot", nargs="*", default=[])
    p.add_argument("--foto"); p.add_argument("--crop")
    p = sub.add_parser("fallita"); p.add_argument("nome"); p.add_argument("motivo"); p.add_argument("file", nargs="+")
    a = ap.parse_args()
    return {"stato": lambda: stato() or 0, "aggiungi": lambda: aggiungi(a), "fallita": lambda: fallita(a)}[a.cmd]()


if __name__ == "__main__":
    sys.exit(main())
